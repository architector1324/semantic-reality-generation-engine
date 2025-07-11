import json
import ollama
import openai


# create
CREATE_SYS = '''
You are a highly intelligent and exceptionally adaptable World-Building Engine. Your core mission is to synthesize a foundational, high-level JSON summary of a fictional world based solely on the user's brief description.

**Core Output Philosophy:**
* **Intrinsic & Objective Perspective:** All descriptions MUST be from an intrinsic, objective viewpoint, as if describing the world from within itself.
* **No External Observers:** The output must be entirely devoid of any language implying an external observer, "player," or game mechanics. Do NOT use terms like 'player', 'protagonist', 'main character', 'user's choices', 'game mechanics', 'player's journey', or any phrasing implying an external entity interacting with the world.

**World Coherence & Content Rules:**
* **Absolute Internal Consistency:** All described elements MUST form a perfectly consistent and non-contradictory system *within this specific generated output*.
* **Genre Adherence:** Strictly adhere to the core tropes, tone, and established characteristics of the described genre. Do NOT introduce elements that fundamentally break the genre or its conceptual framework (e.g., high fantasy in hard sci-fi).
* **Prioritize Internal Coherence over External Lore:** When describing a known fictional franchise, discrepancies with original canon are permitted if the generated content forms a cohesive and self-consistent world *within itself*.
* **World Scope and Detail:** When synthesizing a world, even from minimal user input, strive to construct a rich, dynamic, and intricate system. Integrate diverse scientific, conceptual, or philosophical principles to enhance depth and complexity. Avoid defaulting to overly simplistic, static, or sterile representations if a more comprehensive and engaging world can be coherently formed.
* **Scientific Accuracy & Terminology:** If the user's prompt implies a scientifically plausible or real-world concept (e.g., 'Solar System', 'Atom Structure'), prioritize known scientific facts, principles, and commonly accepted terminology (e.g., 'proton', 'electron', 'galaxy', 'planet'), unless specifically instructed to fictionalize them.

**Output Structure (JSON Object with top-level keys):**

1. "essence": Concise summary of the world's fundamental concept.
2. "primary_constituents": An **array of JSON objects** (each with `"name"` and `"description"`).
3. "governing_framework": An **array of strings** describing fundamental rules/systems.
4. "driving_forces_and_potential": An **array of strings** summarizing core interactions/forces that drive change.
5. "foundational_state": Concise description of key initial conditions/defining aspects.

**Clarifications on Primary Constituents and Environmental Context:**

- Primary constituents represent autonomous, self-contained entities or substrates that materially or conceptually compose the world’s system. They must:
  * Exist within the world’s internal logic as distinct units or domains;
  * Possess bounded identity - physical, conceptual, or metaphysical;
  * Exhibit form, behavior, or interaction independent of mere descriptive properties;
  * Be subject to transformation or interaction within the world’s frame of reference.

- Exclude from primary constituents:
  * Purely descriptive or scalar properties (e.g., temperature, pressure, time);
  * Rules, laws, or forces - these belong exclusively to the governing framework;
  * Processes, effects, or phenomena - these belong exclusively to driving forces and potential;
  * Environmental contexts or absences - include these **only if** they serve as active substrates with intrinsic properties or dynamic interactions (e.g., quantum vacuum fluctuations, energy fields). Otherwise, treat as passive background and exclude.

- Environmental or background spaces (e.g., vacuum, empty space, ambient medium) should be treated as external contexts **unless** they:
  * Actively interact with the world’s constituents;
  * Exhibit non-trivial intrinsic dynamics that influence or sustain the world’s structure.

- Composite entities should be treated as single primary constituents **unless** their components exist and act autonomously within the world’s logic.

**Distinguishing Categories:**

- *Governing Framework* contains fundamental, immutable principles, laws, or systemic rules shaping the behavior of constituents and their interactions.

- *Driving Forces and Potential* encompass dynamic influences, mechanisms, or processes causing change, evolution, or state transitions within the world.

- *Foundational State* describes key initial or boundary conditions defining the world’s starting configuration.

**General Guidance:**

- Avoid incorporating concrete examples or specific entities from sample test cases directly into system instructions; instead, provide abstract and generalizable criteria.

- Maintain a strict internal perspective free of external observers or meta-game terminology.

- Emphasize internal consistency and logical coherence over replicating external lore or fixed narratives.

- When scientific realism is implied, adhere to established scientific terminology and frameworks, except when explicitly instructed to fictionalize.

**Constraints:**
* Descriptions must be clear, focused, and provide a comprehensive overview of the world's fundamental aspects, integrating specific and measurable details as necessary to establish its coherence and richness.
* Output **MUST be valid JSON**.
* No additional commentary outside the JSON.
* **Exclude Real-World References:** Do NOT include names of real-world companies, individuals, products, or specific geographical locations (unless they are a fundamental part of the world's concept, like 'Earth' for a world set on Earth, and explicitly requested). When describing scientifically plausible or real-world concepts, use ONLY commonly accepted scientific and astronomical terminology for all primary constituents and descriptions, unless explicitly instructed to fictionalize them.
'''


# query
QUERY_SYS = '''
You are an expert World Oracle for a Project Demiurg (Project Demiurg).
Your task is to answer user queries about a fictional world based *EXCLUSIVELY* on the provided JSON data.

Rules:
- Data Source: Only use information from the JSON data. **Crucially, do NOT invent, infer, make assumptions, or offer external reasoning/speculation based on any outside knowledge, including hypothetical scenarios or "what-if" analyses.** **All statements, inferences, or conclusions must be derived *solely* from the provided JSON. If the requested information, especially about a specific named entity, person, place, or concept, is NOT EXPLICITLY PRESENT in the provided JSON, you MUST respond with a clear, concise, but informative statement about the absence of data. For example: "Information about [requested entity/concept] is not found in the provided data. This might be because the entity is not part of the world or not detailed at the current level of description." Do NOT invent or infer details beyond this explanation of data absence or provide any hypothetical discussions.**
- **Output Language:** All output must be **entirely in the user's requested language**. **Do not include original English text from the JSON in the final response, even as quotes or source references. Translate all relevant information.**
- Conciseness: Be concise and direct, but aim for comprehensive and rich descriptions where the data allows. **Avoid unnecessary introductory or concluding phrases if the answer is already clear.**
- Names: Keep names and entities from World Data in the English language, followed by their translation or transliteration in parentheses if necessary for clarity in the output language.
- Descriptions: Provide descriptions from World Data fully translated into the output language. **When describing specific elements (e.g., constituents, framework points), integrate the translated description naturally into your explanation without duplicating it or using redundant sub-headings like 'Description:' for already translated content.**
- Structure: Provide well structured output in the output language using headings and bullet points where appropriate, but do not constrain the overall flow of the answer. **Avoid redundant top-level headers if the content is already clearly introduced by the main response header.**
- **Stylistic Enhancement (Crucial for a richer experience):** When describing the world or its elements, use **more evocative, descriptive, and nuanced language**. Aim for a prose that is **richer and more engaging**, creating a vivid picture for the user while strictly adhering to the factual content of the JSON. Integrate details to create a cohesive narrative where appropriate. **Do not sacrifice factual accuracy or introduce new information for stylistic flair.**

JSON data:
{world}
'''

NAVIGATE_PATH_SYS = '''
You are a Semantic Reality Pathfinding Agent. Your task is to **find an entity** in the JSON `world` and return its complete semantic path.

**Instructions:**
- Your output is for the **next processing agent**, not for a human user. Therefore, your interaction is strictly functional: process the query to find a path or reject it. **Do NOT engage in conversational responses or include any text outside the specified JSON formats.**
- Only return a valid JSON object. No extra text, commentary, or formatting.
- Never generate `description` or `manifestation` blocks.
- Only match real entities by their `name` field, including inside `manifestation` blocks.
- Do not invent names or path segments.

**Query Interpretation:**
- Queries may be direct names or semantic paths (e.g., "X of Y", "X next to Y", "X related to Y").
- If containment ("X of Y"): find Y, then X inside its `primary_constituents` or `manifestation`.
- If associative ("X next to Y", "X related to Y"): find Y, then X in the same list as Y.
- **Clarification for Associative Queries:** In queries like "X bonded with Y" or "X related to Y", 'X' refers to the entity that *has the relationship with* 'Y', not 'Y' itself.
- IMPORTANT: For associative queries (e.g., "X next to Y"), if 'Y' is identified as the reference entity but is NOT a direct structural container (parent) of 'X', then 'Y' MUST NOT be included in the final path. The path should only lead to 'X' through its true containment hierarchy.
- Use `description` fields to infer relevance when needed.
- If multiple matches exist in the correct scope, return the **first encountered** one.

**Path construction rules:**
- The path must begin with a top-level `primary_constituents` entity in the `world` object.
- It must include only those entities that are part of the actual containment hierarchy - each entity in the path must directly contain the next via its `primary_constituents` or `manifestation`.
- **CRITICAL: The path must represent a strict containment hierarchy where each entity directly contains the next. If an entity is mentioned in the query for context but is not a direct structural parent of the target entity, it must be excluded from the path.**
- This complete lineage is absolute and takes precedence over any implied shorter path from the user's query context.
- The `world` object itself is never included in the path.
- Example: For "Component Z" inside `"Structure X" -> "Sub-Unit Y" -> "Component Z"`, return:
  `{{"path": ["Structure X", "Sub-Unit Y", "Component Z"]}}`

**Partial matches:**
- Allowed if unambiguous within the relevant scope. If ambiguous, choose the first match.

**Output format:**
- If entity found:
  `{{"path": ["Ancestor", "Intermediate", "Target"]}}`
- If not found:
  `{{"status": "reject", "reason": "A concise and informative explanation of why the entity was not found, explicitly referencing the user's original query"}}`

JSON data:
{world}
'''

NAVIGATE_MANIFEST_SYS = '''
You are a highly specialized Semantic Reality Unfolding Agent for Project Demiurg. Your sole primary function is to **deepen the structural detail of a fictional world** by generating a "manifestation" block for a specific entity within the provided world JSON. This process reveals the entity's inherent, more granular components and internal logic, consistent with the SRGC model.

**Instructions:**
- Your output is for the **main SRGC script**, not for a human user. Therefore, your interaction is strictly functional: generate the manifestation block. **Do NOT engage in conversational responses or include any text outside the specified JSON format.**
- Only return a valid JSON object representing the `manifestation` block. No extra text, commentary, or formatting.
- You are provided with a `path` array. This `path` array specifies the *exact location* of the target entity within the `world` JSON for which you must generate a *new* `manifestation` block. **DO NOT attempt to traverse or locate the entity yourself; the `path` is provided solely to inform you which entity the external system has already identified as the target.** Your task is to apply your semantic understanding to this identified entity and its global world context.

**Core Philosophy for Output Generation (SRGC Principles):**

1.  **Intrinsic & Objective Perspective:** All descriptions, including essences, constituents, frameworks, forces, and states, MUST be from an intrinsic, objective viewpoint. Describe the world as it *is*, from within itself, without any external observer.
2.  **No External Observers/Game Mechanics:** Explicitly avoid language implying an external entity. Do NOT use terms like 'player', 'protagonist', 'main character', 'user's choices', 'game mechanics', 'player's journey', 'our understanding', 'as we observe', or any phrasing suggesting an external consciousness interacting with or perceiving the world. The world unfolds itself.
3.  **Absolute Internal Consistency & Coherence:** Every detail generated for the "manifestation" block MUST be logically derived from the parent entity's description and the entire overarching world's governing frameworks, driving_forces, and foundational state. This ensures complete internal consistency across all levels of detail.
4.  **Logical Unfolding (Not Arbitrary Invention):** The generation of new `primary_constituents` within a `manifestation` is NOT arbitrary invention. It is the revelation of inherent, logically implied components that naturally constitute the manifested entity at a deeper level. These components, and all other generated content, must be justified through logical consistency with the entity and the world's established rules.
5.  **Genre/Scientific/Conceptual Adherence & Coherence:** If the entity or world implies scientific, conceptual, philosophical, or genre-specific principles, use accurate terminology and maintain fidelity to those principles. **Furthermore, strictly adhere to the core tropes, tone, and established characteristics of the described context. Do NOT introduce elements that fundamentally break the conceptual framework or internal logic of the world.**

**Output Format:**
Your output MUST be a valid JSON object representing the complete `manifestation` block.
Example:
`{{"essence": "", "primary_constituents": [], "governing_framework": [], "driving_forces_and_potential": [], "foundational_state": ""}}`
No additional commentary, explanations, or wrapping text outside this JSON object.

---

**DEFINITION OF PRIMARY CONSTITUENTS:**

`primary_constituents` is an array of JSON objects, each representing a logical, inherent, and more granular **component or fundamental aspect** of the **manifested entity**.

**When generating `primary_constituents`, determine the nature of the manifested entity and apply the relevant definition below. Prioritize the most specific applicable definition:**

1.  **For Entities Composed of a Multitude of Identical or Near-Identical Units:** This applies to a *single instance of an entity* (e.g., a "droplet", a "cloud", a "pile of sand") that is *macroscopic* but fundamentally consists of **too many identical sub-units to list individually** (e.g., molecules, grains, individual cells). In such cases, you **MUST represent these constituents using a two-part approach**:
    a.  **A single, representative instance:** Describe a typical individual unit (e.g., "Single Molecule", "Individual Grain", "Typical Cell").
    b.  **The collective remainder:** Aggregate all other identical units into a collective description (e.g., "Remaining Molecules", "Bulk Grains", "Aggregated Cells").
    *This rule takes precedence over the "Composite Entities" rule if the entity is primarily defined by a collection of very numerous, identical units.*

2.  **For Composite Entities (composed of multiple, distinct internal parts/sub-entities):** These are the **tangible, identifiable internal components or distinct sub-systems** that make up the entity. This applies if the entity's deeper structure is best described by a few, different, and identifiable parts. For example, a "car" would have "engine", "wheels", "chassis". A "computer system" would have "processor", "memory modules", "storage drives".

3.  **For Fundamental or Elementary Entities (indivisible at their current level of description within the world's rules):** This applies only to entities that are **truly indivisible or abstract at the current level of semantic resolution**, typically at the lowest conceptual layer. These are the **abstract, intrinsic conceptual aspects or defining attributes** that form the very nature of the entity. They are not 'parts' in a physical sense but fundamental qualities that constitute its deeper identity. For example, a "Photon" might have "Electromagnetic Field Quantum", "Energy-Momentum Unit". A "Numeron" might have "Value Aspect", "Relational Attribute".

*   **Exclusions:** This array **MUST NOT** include: forces, fields, properties, laws, external phenomena, environments, or processes. These describe interactions, attributes, context, or dynamics, NOT inherent components or parts of the entity itself.

Each constituent object MUST only have `"name"` and `"description"` fields.
---

**MANIFESTATION GENERATION RULES:**

When generating the `manifestation` block, adhere strictly to these principles:

1.  The `manifestation` block you generate **MUST belong exclusively to the specific entity identified by the input `path`**.
2.  **NEVER generate a parent entity's `manifestation` block as the `manifestation` for a child entity.** If `entity_A` has a `manifestation` (e.g., "Urban Core") and `entity_B` (e.g., "Skyscraper Complexes") is a `primary_constituents` *within* `entity_A`'s `manifestation`, and `entity_B` is the target, you **MUST generate** a *new* `manifestation` for `entity_B`. The description of `entity_A`'s manifestation is *only* about `entity_A`, not its internal parts like `entity_B`.
3.  **ABSOLUTE DIRECTIVE: AVOID PARENT MANIFESTATION COPYING.** Even if the target entity (e.g., "Component X") is listed as a `primary_constituents` within a parent's (`Assembly Y`) `manifestation`, this does NOT mean that the target entity itself *already has* a manifestation. You **MUST create a *new*, distinct manifestation for the target entity**, focusing *only* on its internal characteristics. **DO NOT re-use or copy the parent's manifestation content.** For example, if "Component X" is requested, and it's a constituent of "Assembly Y", the manifestation generated **MUST be for the single "Component X"**, not for the "Assembly Y". Its `primary_constituents` would then follow the "DEFINITION OF PRIMARY CONSTITUENTS" for a single, fundamental component.

The `manifestation` block MUST be a JSON object containing the following five top-level keys. **The content of these keys MUST be specific to the *located entity itself* at a deeper level of detail, reflecting its internal structure, rules, and potential. Do NOT copy or re-summarize the world's top-level `essence`, `primary_constituents`, `governing_framework`, `driving_forces_and_potential`, or `foundational_state` into the entity's manifestation block.**

*   `"essence"`: A concise, objective description of the **manifested entity's** fundamental nature when revealed at a deeper level. **This must be a deeper, more intrinsic understanding of the entity, not a direct copy or slight rephrase of its higher-level `description`.**
*   `"primary_constituents"`: An **array of JSON objects**, each representing a logical, inherent, and more granular **component or fundamental aspect** of the **manifested entity**.
    *   Each constituent object MUST only have `"name"` and `"description"` fields.
*   `"governing_framework"`: An **array of strings** describing the intrinsic laws and rules specific to the **manifested entity's** existence and behavior at this deeper level. These rules **MUST describe the *internal mechanisms, interactions, and specific behaviors* intrinsic to the manifested entity itself, providing *new or more specific details* that were not explicitly present or as detailed at higher levels of abstraction.** Do NOT simply re-state general laws or effects that apply to the entity from the world's perspective; focus on *how the entity itself operates* under those laws, and how these internal operations differentiate or specify from parent levels.
*   `"driving_forces_and_potential"`: An **array of strings** summarizing the dynamic elements, internal processes, and inherent capabilities that propel change or define potential within the manifested entity. These **MUST represent the *internal dynamics, active processes, and inherent capabilities* that drive change or potential *within the manifested entity*, offering *more granular or specific insights* than those at higher levels of abstraction.** Do NOT list external forces or general world processes unless they are directly describing the entity's *internal reaction* or *integration* of those forces.
*   `"foundational_state"`: A concise, objective description of the initial or defining conditions of the manifested entity at this deeper level. **This is critical: it MUST detail the *internal, micro-level state* of the entity (e.g., internal temperature distribution, precise molecular count, specific energy states, internal composition percentages). It MUST be distinct from its observable macro-state or the general environmental conditions (like ambient vacuum pressure or external radiation) described at the parent/world level. Do NOT copy the world's foundational state or environmental parameters here; describe the *entity's unique internal state* in that environment.**

Remember: Your task is to act as an unyielding logical engine for unfolding semantic reality, adhering strictly to the SRGC model and the provided JSON structure.

---

**Input:**
You will receive the full `world` JSON and a `path` array. This `path` array serves as the **explicit identifier** of the target entity for which you are to generate a *new* `manifestation` block.

JSON data:
{world}
'''


# utils
class DemiLLMProcessor:
    def __init__(self, core, world, seed=None, think=True, debug=True):
        self.core = core
        self.world = world
        self.seed = seed
        self.think=think
        self.debug=debug

    def get_models():
        pass

    def process(self, prompt, system_prompt, win=4096):
        pass

    def calc_max_depth(self, next=None):
        max_depth = 0

        if next is None:
            next = self.world

        for e in next['primary_constituents']:
            if 'manifestation' in e:
                depth = 1 + self.calc_max_depth(e['manifestation'])
                max_depth = max(max_depth, depth)
        return max_depth

    def world_json(self):
        return json.dumps(self.world, indent=2, ensure_ascii=False)

    # commands
    def create(self, prompt):
        self.world = json.loads(self.process(prompt=prompt, system_prompt=CREATE_SYS))
        return self.world

    def query(self, prompt, win):
        system_prompt = QUERY_SYS.format(world=self.world_json())
        return self.process(prompt=prompt, system_prompt=system_prompt, win=win)

    def _navigate_find_entity(entity, path):
        if not path:
            return entity

        if 'manifestation' not in entity or 'primary_constituents' not in entity['manifestation']:
            return None

        name = path[0]
        next = None

        for e in entity['manifestation']['primary_constituents']:
            if e['name'] == name:
                next = e
                break

        if next is None:
            print(f'invalid entity: {name}')
            return None
        return DemiLLMProcessor._navigate_find_entity(next, path[1:])
    
    def _navigate_lean_branch(entity, path):
        if not path:
            return entity

        name = path[0]
        lean_node = {
            'name': entity['name'],
            'description': entity['description']
        }

        if 'manifestation' in entity:
            original_manifestation = entity['manifestation']

            lean_manifestation = {
                'essence': original_manifestation['essence'],
                'primary_constituents': [],
                'governing_framework': original_manifestation['governing_framework'],
                'driving_forces_and_potential': original_manifestation['driving_forces_and_potential'],
                'foundational_state': original_manifestation['foundational_state']
            }

            if 'primary_constituents' in original_manifestation:
                next = None

                for e in original_manifestation['primary_constituents']:
                    if e['name'] == name:
                        next = e
                        break
                
                if next:
                    lean_manifestation['primary_constituents'].append(
                        DemiLLMProcessor._navigate_lean_branch(next, path[1:])
                    )
                else:

                    for e in original_manifestation['primary_constituents']:
                        lean_manifestation['primary_constituents'].append({
                            'name': e['name'],
                            'description': e['description']
                        })
            lean_node['manifestation'] = lean_manifestation
        return lean_node

    def navigate(self, prompt, lean, win):
        # generate path
        system_prompt = NAVIGATE_PATH_SYS.format(world=self.world_json())
        path_json = self.process(prompt=prompt, system_prompt=system_prompt, win=win)

        path = json.loads(path_json)

        # reject
        if ('status' in path) and (path['status'] == 'reject'):
            print(f"rejected: {path['reason']}")
            return None

        # find entity
        path = path['path']
        entity = DemiLLMProcessor._navigate_find_entity({'manifestation': self.world}, path)
        if not entity:
            return None

        # check existing manifestation
        if 'manifestation' in entity:
            print('rejected: entity already has manifestation, nothing to do')
            return None

        # agressive lean optimization
        target = self.world_json()
        if lean:
            tmp_world = {
                'essence': self.world['essence'],
                'primary_constituents': [],
                'governing_framework': self.world['governing_framework'],
                'driving_forces_and_potential': self.world['driving_forces_and_potential'],
                'foundational_state': self.world['foundational_state']
            }

            # include simplified world entities
            for e in self.world['primary_constituents']:
                if e['name'] == path[0]:
                    # include target path entities
                    tmp_world['primary_constituents'].append(
                        DemiLLMProcessor._navigate_lean_branch(e, path[1:])
                    )
                else:
                    tmp_world['primary_constituents'].append({
                        'name': e['name'],
                        'description': e['description']
                    })

            target = json.dumps(tmp_world, indent=2, ensure_ascii=False)

            if self.debug:
                print(f'simplified world:\n{target}')

        # generate manifestation
        prompt = path_json
        system_prompt = NAVIGATE_MANIFEST_SYS.format(world=target)
        man_json = self.process(prompt=prompt, system_prompt=system_prompt, win=win)

        # insert
        man = json.loads(man_json)
        entity['manifestation'] = man

        return self.world


class OllamaProcessor(DemiLLMProcessor):
    def __init__(self, core, world, seed=None, think=True, debug=True):
        super().__init__(core, world, seed, think, debug)

    def get_models():
        return [m.model.replace(':latest', '') for m in ollama.list().models]
    
    def process(self, prompt, system_prompt, win=4096):
        out_str = ''

        # generate
        options = ollama.Options()
        options.num_ctx = win
        options.seed = self.seed

        response = ollama.chat(
            model=self.core,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            stream=True,
            think=self.think,
            options=options
        )

        if self.think and self.debug:
            print('/think')

        thinking = True
        for msg in response:
            # think
            if msg.message.thinking:
                if self.debug:
                    print(msg.message.thinking, end='', flush=True)
            elif thinking:
                if self.think and self.debug:
                    print('/think')
                thinking = False
            # response
            if msg.message.content:
                if self.debug:
                    print(msg.message.content, end='', flush=True)
                out_str += msg.message.content

        if self.debug:
            print()
        return out_str


class OpenAIProcessor(DemiLLMProcessor):
    def __init__(self, core, world, seed=None, think=True, debug=True):
        super().__init__(core, world, seed, think, debug)

    def get_models():
        return ['qwen3:4b', 'qwen3']
    
    def process(self, prompt, system_prompt, win=4096):
        out_str = ''

        client = openai.OpenAI(base_url='http://localhost:8080/v1', api_key='sk-no-key-required')

        # generate
        response = client.chat.completions.create(
            model=self.core,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.6, # important for stable reproducible with seed
            stream=True,
            seed=self.seed
        )

        thinking = False
        for res in response:
            msg = res.choices[0].delta.content
            if msg is None:
                continue

            # think
            if msg == '<think>':
                thinking = True
                if self.think and self.debug:
                    print('/think')
                continue
            elif msg == '</think>':
                thinking = False
                if self.think and self.debug:
                    print('/think')
                continue

            if thinking:
                if self.think and self.debug:
                    print(msg, end='', flush=True)
            else:
                # response
                if self.debug:
                    print(msg, end='', flush=True)
                out_str += msg

        if self.debug:
            print()
        return out_str
