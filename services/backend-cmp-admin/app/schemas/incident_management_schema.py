from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Literal, Optional
from datetime import datetime


class Step(BaseModel):
    step_name: str
    step_description: str


class WorkflowStage(BaseModel):
    stage_name: str
    steps: List[Step] = []


class IncidentCreate(BaseModel):
    incident_name: str
    incident_type: str
    incident_sensitivity: Literal["low", "medium", "high"]
    description: str

    status: Optional[Literal["draft", "published", "in_progress", "closed"]] = "draft"

    current_stage: str
    workflow: List[WorkflowStage]

    assignee: Optional[str] = None
    template_used: Optional[str] = None

    date_occurred: Optional[datetime] = None
    date_discovered: Optional[datetime] = None
    deadline: Optional[datetime] = None
    date_closed: Optional[datetime] = None
    created_at: Optional[datetime] = None

    data_element: Optional[List[str]] = None

    regulatory_reported: Optional[bool] = None
    regulatory_reported_date: Optional[datetime] = None
    regulatory_authority: Optional[str] = "DPIA"
    compliance_standard: Optional[str] = "DPDPA"

    notification_needed: Optional[bool] = None
    notification_sent: Optional[bool] = None
    notification_sent_date: Optional[datetime] = None

    affected_population: Optional[int] = None
    mitigation_steps: Optional[List[str]] = None

    @field_validator("workflow")
    @classmethod
    def validate_workflow_non_empty(cls, value: List[WorkflowStage]):
        if not value or len(value) == 0:
            raise ValueError("workflow cannot be empty")

        names = [s.stage_name for s in value]
        if len(names) != len(set(names)):
            raise ValueError("workflow stage_name values must be unique")
        return value

    @model_validator(mode="after")
    def add_default_notification_workflow_stages(self):
        if self.notification_sent:
            stage_names = [s.stage_name for s in self.workflow]

            if "notifying" not in stage_names:
                self.workflow.append(WorkflowStage(stage_name="notifying", steps=[]))

            if "closure" not in stage_names:
                self.workflow.append(WorkflowStage(stage_name="closure", steps=[]))

            if not self.mitigation_steps:
                raise ValueError("mitigation_steps must be provided when notification_sent is True")

            final_stage_names = [s.stage_name for s in self.workflow]
            if len(final_stage_names) != len(set(final_stage_names)):
                raise ValueError("Workflow stage_name values must be unique after default stages are added.")
        return self

    @field_validator("current_stage")
    @classmethod
    def validate_current_stage(cls, value: str, info):
        data = info.data
        workflow = data.get("workflow")
        if workflow:
            stage_names = [s.stage_name for s in workflow]
            if value not in stage_names:
                raise ValueError(f"current_stage '{value}' must be one of {stage_names}")
            if value != stage_names[0]:
                raise ValueError(f"current_stage must be the first workflow stage: '{stage_names[0]}'")
        return value


class AddStepRequest(BaseModel):
    stage_name: str
    step: Step


class UpdateStageRequest(BaseModel):
    new_stage: str
