import json
import re
import uuid
from datetime import datetime, timezone

# ----------------------------------------------------------------------
# 1. ARCHITECTED DECLARATIVE REGISTRY (registry.json simulation)
# ----------------------------------------------------------------------
REGISTRY = {
    "UPDATE_USER_PROFILE": {
        "version": "1.0.0",
        "status": "ACTIVE",
        "parameters": {
            "email": {
                "required": True,
                "regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            },
            "role": {
                "required": True,
                "enum": ["Admin", "User", "Viewer"]
            }
        },
        "routing": {
            "on_success": "identity-service/v1/updateUser",
            "on_failure": "governance-service/v1/parameter-error"
        }
    }
}

class RossOSMiddleware:
    def __init__(self, registry: dict):
        self.registry = registry

    # ----------------------------------------------------------------------
    # 2. STAGE 1: THE NORMALIZATION ENGINE
    # ----------------------------------------------------------------------
    def _normalize(self, raw_input: str, extracted_action: str, extracted_vars: dict) -> str:
        """
        Enforces Rule Groups A, B, and C. Strips phatic noise, flattens markdown,
        and compiles the string into the deterministic Ross-OS Canonical Format.
        """
        # Rule 1.1 & 1.2: Flattening, whitespace normalization, markdown stripping
        clean_text = raw_input.strip()
        clean_text = re.sub(r"[\*\_`#\-]", "", clean_text)  # Strip markdown markers
        clean_text = re.sub(r"\s+", " ", clean_text)       # Flatten whitespaces/newlines
        
        # Rule 1.3: Enforce ASCII/UTF-8 clean string representation
        clean_text = clean_text.encode("utf-8", errors="ignore").decode("utf-8")
        
        # Rule Group C: Compile into Canonical Format String
        # Formula: [Action]. [Key 1]: [Value 1]. [Key 2]: [Value 2].
        formatted_action = extracted_action.replace("_", " ").title()
        param_strings = [f"{k.capitalize()}: {v}" for k, v in extracted_vars.items()]
        canonical_string = f"{formatted_action}. {'. '.join(param_strings)}."
        
        return canonical_string

    # ----------------------------------------------------------------------
    # 3. STAGE 2 & 3: VALIDATION ENGINE & GOVERNANCE ROUTING
    # ----------------------------------------------------------------------
    def process_transaction(self, raw_input: str, source_engine: str, raw_intent: str, extracted_vars: dict) -> dict:
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Base Blueprint Payload
        payload = {
            "$schema": "https://rossconsultancy.io/schemas/v0.1/payload.json",
            "metadata": {
                "transaction_id": transaction_id,
                "timestamp": timestamp,
                "source_engine": source_engine
            },
            "semantic_intent": {
                "primary_action": raw_intent,
                "confidence_score": 1.0,  # Assumed absolute match for pipeline trace
                "parameters": {
                    "key_variables": extracted_vars
                }
            },
            "payload_normalization": {
                "raw_token_count": len(raw_input.split()),
                "clean_text_content": "",
                "structural_anomalies_detected": False
            },
            "governance_routing": {
                "validation_status": "APPROVED",
                "next_canonical_hop": ""
            }
        }

        # --- FIREWALL 3: GOVERNANCE FIREWALL ---
        if raw_intent not in self.registry or self.registry[raw_intent]["status"] != "ACTIVE":
            payload["governance_routing"].update({
                "validation_status": "ESCALATED",
                "next_canonical_hop": "governance-service/v1/manual-review"
            })
            payload["error_context"] = {
                "error_class": "GOVERNANCE_ERROR",
                "error_code": "ROSS-VAL-003",
                "error_message": f"Action [{raw_intent}] is unknown or inactive in the current registry manifest.",
                "offending_fields": ["primary_action"],
                "origin_stage": "GOVERNANCE",
                "timestamp": timestamp
            }
            return payload

        action_spec = self.registry[raw_intent]
        
        # Execute Normalization to string right after basic intent check pass
        payload["payload_normalization"]["clean_text_content"] = self._normalize(raw_input, raw_intent, extracted_vars)

        # --- FIREWALL 1 & 2: STRUCTURAL & SEMANTIC FIREWALLS ---
        errors = []
        offending_fields = []
        spec_params = action_spec["parameters"]

        for param_name, constraints in spec_params.items():
            # Check presence (Structural)
            if constraints["required"] and param_name not in extracted_vars:
                errors.append(f"Missing required structural parameter [{param_name}]")
                offending_fields.append(param_name)
                continue
            
            value = extracted_vars.get(param_name)
            
            # Check Semantic Constraints if value exists
            if value:
                if "regex" in constraints:
                    if not re.match(constraints["regex"], str(value)):
                        errors.append(f"Parameter [{param_name}] fails strict regex validation constraint.")
                        offending_fields.append(param_name)
                
                if "enum" in constraints:
                    if value not in constraints["allowed_values"]:
                        errors.append(f"Parameter [{param_name}] must explicitly match allowed enums: {constraints['allowed_values']}.")
                        offending_fields.append(param_name)

        # Handle Pipeline Violations
        if errors:
            payload["governance_routing"].update({
                "validation_status": "REJECTED",
                "next_canonical_hop": action_spec["routing"]["on_failure"]
            })
            payload["error_context"] = {
                "error_class": "PARAMETER_ERROR" if offending_fields else "STRUCTURAL_ERROR",
                "error_code": "ROSS-VAL-002",
                "error_message": "; ".join(errors),
                "offending_fields": offending_fields,
                "origin_stage": "SEMANTIC",
                "timestamp": timestamp
            }
        else:
            # Happy Path Routing
            payload["governance_routing"]["next_canonical_hop"] = action_spec["routing"]["on_success"]

        return payload

# ----------------------------------------------------------------------
# 4. RUNTIME VERIFICATION (The End-to-End Test Execution Trace)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    engine = RossOSMiddleware(REGISTRY)
    
    # Trace 1: The Locked Happy Path Input
    gpt_input = "Hey there! Sure, I can help you update that user profile... email is alex@example.com... role is Admin..."
    extracted_intent = "UPDATE_USER_PROFILE"
    extracted_data = {"email": "alex@example.com", "role": "Admin"}
    
    print("--- TRACE 1: VALID TRANSACTON ---")
    output_payload = engine.process_transaction(gpt_input, "gpt", extracted_intent, extracted_data)
    print(json.dumps(output_payload, indent=2))
    
    # Trace 2: The Failure Case (Malicious/Malformed Role Input)
    malformed_data = {"email": "alex@example.com", "role": "RootSuperAdmin"}
    print("\n--- TRACE 2: SEMANTIC FIREWALL BREACH (REJECTED) ---")
    fail_payload = engine.process_transaction(gpt_input, "gpt", extracted_intent, malformed_data)
    print(json.dumps(fail_payload, indent=2))
