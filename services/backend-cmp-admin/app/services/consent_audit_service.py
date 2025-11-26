import json
import hashlib
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec


class ConsentAuditService:
    def __init__(self, crud, public_key_pem: str):
        self.crud = crud
        self.public_key = serialization.load_pem_public_key(public_key_pem.encode())

    def _sha256(self, s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def _verify_signature(self, record_hash: str, signature_b64: str) -> bool:
        try:
            signature = base64.b64decode(signature_b64)
            self.public_key.verify(signature, record_hash.encode("utf-8"), ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False

    async def get_dp_audit_history(self, dp_id: str, current_user: str = None):
        df_id = current_user["df_id"]
        cursor = self.crud.get_logs(dp_id, df_id)
        logs = await cursor.to_list(length=None)

        prev_record_hash = None
        verified_logs = []

        for log in logs:
            entry = log.copy()
            entry["_id"] = str(entry["_id"])

            clean = log.copy()
            for f in ["_id", "canonical_record", "data_hash", "prev_record_hash", "record_hash", "signature", "signed_with_key_id"]:
                clean.pop(f, None)

            canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"))
            calc_data_hash = self._sha256(canonical)

            data_ok = calc_data_hash == log["data_hash"]

            expected_chain_hash = self._sha256((prev_record_hash or "") + log["data_hash"] + log["timestamp"])
            chain_ok = expected_chain_hash == log["record_hash"]

            signature_ok = self._verify_signature(log["record_hash"], log["signature"])

            tampered = not (data_ok and chain_ok and signature_ok)
            entry["tampered"] = tampered
            entry["integrity"] = {
                "data_hash_ok": data_ok,
                "chain_ok": chain_ok,
                "signature_ok": signature_ok,
            }
            verified_logs.append(entry)
            prev_record_hash = log["record_hash"]

        return verified_logs

    async def get_dp_audit_history_internal(self, dp_id: str, df_id: str = None):
        cursor = self.crud.get_logs(dp_id, df_id)
        logs = await cursor.to_list(length=None)

        prev_record_hash = None
        verified_logs = []

        for log in logs:

            entry = log.copy()
            entry["_id"] = str(entry["_id"])

            clean = log.copy()
            for f in ["_id", "canonical_record", "data_hash", "prev_record_hash", "record_hash", "signature", "signed_with_key_id"]:
                clean.pop(f, None)

            canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"))
            calc_data_hash = self._sha256(canonical)

            data_ok = calc_data_hash == log["data_hash"]

            expected_chain_hash = self._sha256((prev_record_hash or "") + log["data_hash"] + log["timestamp"])
            chain_ok = expected_chain_hash == log["record_hash"]

            signature_ok = self._verify_signature(log["record_hash"], log["signature"])

            tampered = not (data_ok and chain_ok and signature_ok)

            entry["tampered"] = tampered
            entry["integrity"] = {
                "data_hash_ok": data_ok,
                "chain_ok": chain_ok,
                "signature_ok": signature_ok,
            }

            verified_logs.append(entry)
            prev_record_hash = log["record_hash"]

        return verified_logs
