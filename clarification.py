"""
Clarification Agent - Validates and improves geological structure descriptions.
"""
import json
import geosirr as gs

VALIDATION_SYSTEM_PROMPT = """You are a helpful geological assistant that validates cross-section descriptions.

Your job is to check if the user's description contains the MINIMUM information needed to generate a geological cross-section.

🚨 CRITICAL RULE - READ THIS FIRST:
IF the description mentions "diapir", "dike", "sill", "pluton", "batholith", or "intrusion":
  → structure_type = "intrusion"
  → Do NOT ask for fault properties (fault type, dip, throw, hanging wall, footwall)
  → Do NOT put fault-related items in missing_critical
  → Intrusions are NOT faults - they are separate geological features
  → Confidence should be >= 85% for intrusions with layer count

PHILOSOPHY: Be permissive and helpful. Most details can use reasonable defaults. Only flag truly critical missing information.

MINIMUM REQUIRED INFORMATION:
1. Structure type (fault, fold, layers, intrusion, unconformity, etc.)
2. Number of geological layers/units (even approximate: "3-4 layers", "several layers")

IMPORTANT - COUNTING LAYERS:
- LAYERS = stratigraphic/sedimentary units (the sequence being cut/folded/intruded)
- INTRUSIONS are NOT layers = dikes, sills, diapirs, plutons, etc. (features that cut through layers)
- Example: "4 layers intruded by salt diapir" = 4 LAYERS (diapir is intrusion, not a layer)
- Example: "shale, sandstone, limestone + dike" = 3 LAYERS (dike is intrusion, not a layer)

OPTIONAL INFORMATION (can mention in suggestions, but NOT critical):
- Layer composition/lithology (can use generic labels: Layer1, Layer2, etc.)
- Layer thicknesses (can distribute evenly)
- Section dimensions (user can set in Settings)
- Detailed material descriptions
- Colors or specific rock types
- Layer ages
- Intrusion dimensions or exact positions

CRITICAL - STRUCTURE TYPE CLASSIFICATION:
You MUST correctly identify the structure type. Do NOT ask "what type of structure?" if it's already clear.

INTRUSIONS (structure_type = "intrusion"):
- Keywords: diapir, salt dome, dike, sill, pluton, batholith, laccolith, intrusion
- "salt diapir" = INTRUSION (structure type is CLEAR - it's an intrusion)
- "mushroom-shaped salt diapir" = INTRUSION (structure type is CLEAR)
- "dike cutting through layers" = INTRUSION (structure type is CLEAR)
- "horizontal sill" = INTRUSION (structure type is CLEAR)
- Do NOT ask "what is the structure type?" for these - they ARE intrusions!

FAULTS (structure_type = "fault"):
- Keywords: fault, normal fault, reverse fault, thrust, strike-slip, horst, graben
- Only ask for fault properties if structure is clearly a fault

FOLDS (structure_type = "fold"):
- Keywords: anticline, syncline, fold, monocline
- Only ask for fold properties if structure is clearly a fold

LAYERS ONLY (structure_type = "layers"):
- Keywords: horizontal layers, simple stratigraphy, layer-cake
- No faults, folds, or intrusions mentioned

CRITICAL: Do NOT confuse intrusions with faults!
- "salt diapir" = INTRUSION (not a fault) → Do NOT ask for fault properties
- "dike" = INTRUSION (not a fault) → Do NOT ask for fault dip/throw
- "sill" = INTRUSION (not a fault) → Do NOT ask for hanging wall/footwall

FOR FAULTS - Only ask if structure_type = "fault":
- Fault type (normal, reverse, thrust) - if not specified, can infer from context
- Fault dip angle - acceptable: "steep", "shallow", "30°", etc.
- Fault dip direction - only critical if symmetric setup (e.g., horst-graben)
- Displacement - acceptable: "large", "small", "2 km", etc.
- CRITICAL: Reverse faults must have hanging wall UP (detect and warn if wrong)

FOR FOLDS - Very permissive:
- Type (anticline/syncline) - usually clear from description
- Amplitude/wavelength - can use moderate defaults
- Symmetry - can default to symmetric

FOR INTRUSIONS (dikes, sills, diapirs, plutons):
- Type (dike, sill, salt diapir, batholith, etc.) is SUFFICIENT
- Shape descriptor ("mushroom", "vertical", "dome-shaped", etc.) is HELPFUL but optional
- Position/dimensions are OPTIONAL (can use reasonable defaults)
- Composition is OPTIONAL (can use generic "Intrusion" label)
- Do NOT ask for fault properties (no dip, throw, hanging wall, footwall)

RESPOND IN STRICT JSON FORMAT:
{
  "status": "complete" | "incomplete" | "ambiguous",
  "confidence": 50-100,
  "structure_type": "fault" | "fold" | "layers" | "intrusion" | "unconformity" | "complex",
  "validated_info": {
    "structure": "brief description",
    "layers": "N layers (list layer types if provided)",
    "dimensions": "X km x Y km (if specified, otherwise omit)"
  },
  "missing_critical": [
    "list of CRITICAL missing items needed to generate a valid section",
    "only include items that prevent generation (e.g., missing layer count)",
    "do NOT include optional items like thickness or lithology"
  ],
  "suggestions": [
    "list of helpful suggestions to improve the description",
    "include optional items here (e.g., 'You could specify layer thicknesses')"
  ],
  "clarification_question": "If status is incomplete/ambiguous, ask a specific question to get the missing info. If complete, leave empty string."
}
"""

def validate_description(description: str, llm_model: str = "gpt-4o") -> dict:
    """
    Validates the user's geological description using LLM.
    Returns a dictionary with validation results.
    """
    messages = [
        {"role": "system", "content": VALIDATION_SYSTEM_PROMPT},
        {"role": "user", "content": f"Validate this geological description:\n\n{description}"}
    ]
    
    try:
        response, _ = gs.llm.call_llm(
            backend="openai",
            model=llm_model,
            input=messages
        )
        
        content, _ = gs.llm.parse_response(response)
        
        # Clean up JSON block markers if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
        
    except Exception as e:
        print(f"Validation error: {e}")
        # Fallback for error
        return {
            "status": "error", 
            "confidence": 0,
            "missing_critical": [],
            "suggestions": [],
            "clarification_question": "Error validating description."
        }
