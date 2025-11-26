from typing import Dict, Any, Optional
from datetime import datetime, timezone
import aio_pika
from app.services.webhooks_service import WebhooksService
from app.core.logger import app_logger


class EventClassificationService:
    def __init__(self, webhooks_service: WebhooksService):
        self.webhooks_service = webhooks_service

    def _filter_payload(self, event_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms the verbose incoming consent event payload into the required concise format.
        Removes fields like hash IDs and internal metadata.
        """
        filtered_payload = event_payload.copy()

        CONSENT_FIELDS_TO_REMOVE = [
            "purpose_hash_id",
            "consent_mode",
            "cross_border",
            "consent_timestamp",
            "retention_timestamp",
            "legal_mandatory",
            "service_mandatory",
            "reconsent",
        ]

        if "data_elements" in filtered_payload and isinstance(filtered_payload["data_elements"], list):
            new_data_elements = []
            for de in filtered_payload["data_elements"]:
                new_de = de.copy()
                new_de.pop("de_hash_id", None)
                new_de.pop("de_status", None)
                if "consents" in new_de and isinstance(new_de["consents"], list):
                    new_consents = []
                    for consent in new_de["consents"]:
                        new_consent = consent.copy()
                        for field in CONSENT_FIELDS_TO_REMOVE:
                            new_consent.pop(field, None)
                        new_consents.append(new_consent)
                    new_de["consents"] = new_consents

                new_data_elements.append(new_de)

            filtered_payload["data_elements"] = new_data_elements

        return filtered_payload

    async def classify_and_publish_event(self, event_payload: Dict[str, Any], channel: Optional[aio_pika.Channel] = None):
        event_type_from_payload = event_payload.get("event_type", "UNKNOWN_EVENT").upper()
        app_logger.info(f"Processing event classification for event_type: {event_type_from_payload}")

        filtered_event = self._filter_payload(event_payload)

        classified_event = self._perform_classification(filtered_event)

        dp_id = event_payload.get("dp_id")
        df_id = event_payload.get("df_id")

        if not df_id:
            app_logger.error("Event classification failed: df_id is missing from event payload")
            return {"status": "failed", "reason": "df_id missing"}

        all_webhooks_for_df = await self.webhooks_service.list_webhooks(current_user={"df_id": df_id})

        if not all_webhooks_for_df:
            app_logger.info(f"No webhooks found for df_id: {df_id}. Event classified but not published.")
            return {"status": "classified", "reason": "no webhooks found"}

        published_event_ids = []

        all_dpr_ids = set()
        for purpose in event_payload.get("purposes", []):
            for dp in purpose.get("data_processors", []):
                if isinstance(dp, dict):
                    dp_id_val = dp.get("data_processor_id")
                    if dp_id_val:
                        all_dpr_ids.add(dp_id_val)
                elif isinstance(dp, str):
                    all_dpr_ids.add(dp)

        for de in event_payload.get("data_elements", []):
            if "consents" in de and isinstance(de["consents"], list):
                for consent in de["consents"]:
                    for dp in consent.get("data_processors", []):
                        if isinstance(dp, dict):
                            dp_id_val = dp.get("data_processor_id")
                            if dp_id_val:
                                all_dpr_ids.add(dp_id_val)
                        elif isinstance(dp, str):
                            all_dpr_ids.add(dp)

        is_data_element_event = "data_elements" in classified_event and not classified_event.get("purposes")

        for webhook_config in all_webhooks_for_df:
            if webhook_config.get("webhook_for") != "df":
                continue

            webhook_id = str(webhook_config["_id"])
            subscribed_events = [e.upper() for e in webhook_config.get("subscribed_events", [])]

            if event_type_from_payload not in subscribed_events:
                app_logger.debug(f"DF webhook {webhook_id} not subscribed to event type: {event_type_from_payload}")
                continue

            app_logger.info(f"Publishing event to DF webhook {webhook_id} for df_id: {df_id}")

            inserted_id = await self.webhooks_service._publish_webhook_event(
                webhook_id=webhook_id, df_id=df_id, dp_id=dp_id, payload=classified_event, channel=channel
            )

            published_event_ids.append(str(inserted_id))

        for webhook_config in all_webhooks_for_df:
            if webhook_config.get("webhook_for") != "dpr":
                continue

            webhook_id = str(webhook_config["_id"])
            webhook_dpr_id = webhook_config.get("dpr_id")
            subscribed_events = [e.upper() for e in webhook_config.get("subscribed_events", [])]

            if event_type_from_payload not in subscribed_events:
                app_logger.debug(f"DPR webhook {webhook_id} not subscribed to event type: {event_type_from_payload}")
                continue

            app_logger.info(f"Attempting to publish event to DPR webhook {webhook_id} for dpr_id: {webhook_dpr_id}")

            if webhook_dpr_id and webhook_dpr_id in all_dpr_ids:
                payload_for_dpr = {**classified_event, "event_for": "dpr", "data_processor_id": webhook_dpr_id}

                if is_data_element_event:
                    dpr_specific_data_elements = []
                    for de in classified_event.get("data_elements", []):
                        filtered_consents = [
                            c
                            for c in de.get("consents", [])
                            if any(dp_item.get("data_processor_id") == webhook_dpr_id for dp_item in c.get("data_processors", []))
                        ]
                        if filtered_consents:
                            new_de = {**de, "consents": filtered_consents}
                            dpr_specific_data_elements.append(new_de)

                    if not dpr_specific_data_elements:
                        app_logger.debug(f"No DPR-specific data elements found for webhook {webhook_id}. Skipping.")
                        continue
                    payload_for_dpr["data_elements"] = dpr_specific_data_elements
                else:
                    dpr_specific_purposes = [
                        p
                        for p in classified_event.get("purposes", [])
                        if any(dp_item.get("data_processor_id") == webhook_dpr_id for dp_item in p.get("data_processors", []))
                    ]
                    if not dpr_specific_purposes:
                        app_logger.debug(f"No DPR-specific purposes found for webhook {webhook_id}. Skipping.")
                        continue
                    payload_for_dpr["purposes"] = dpr_specific_purposes

                inserted_id = await self.webhooks_service._publish_webhook_event(
                    webhook_id=webhook_id, df_id=df_id, dp_id=dp_id, payload=payload_for_dpr, channel=channel
                )

                published_event_ids.append(str(inserted_id))
            else:
                app_logger.info(
                    f"Skipping DPR webhook {webhook_id}: Configured DPR ID '{webhook_dpr_id}' not found in event payload (looking for 'data_processor_id' in purposes/data_elements) {list(all_dpr_ids)}."
                )

        app_logger.info(f"Event classification and publishing complete. Published event IDs: {published_event_ids}")
        return {"status": "classified and published", "event_ids": published_event_ids}

    def _perform_classification(self, event_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs classification based on event_type.
        Adds a 'classification' field and timestamp to the event payload.
        """
        classified_payload = event_payload.copy()
        event_type = classified_payload.get("event_type")

        if event_type in ["consent_given", "consent_granted"]:
            classified_payload["classification"] = "approved"
        elif event_type == "consent_withdrawn":
            classified_payload["classification"] = "withdrawn"
        elif event_type == "consent_expired":
            classified_payload["classification"] = "expired"
        elif event_type == "data_erasure_retention_triggered":
            classified_payload["classification"] = "data_erasure_retention_triggered"
        elif event_type == "data_erasure_manual_triggered":
            classified_payload["classification"] = "data_erasure_manual_triggered"
        elif event_type == "data_update_requested":
            classified_payload["classification"] = "data_update_requested"
        else:
            classified_payload["classification"] = "unclassified"

        classified_payload["classification_timestamp"] = datetime.now(timezone.utc).isoformat()

        return classified_payload
