GRAPH_FIELD_SEP = "<SEP>"

PROMPTS = {}

PROMPTS["DEFAULT_LANGUAGE"] = "Chinese"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"
PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["疾病", "临床表现", "身体", "医疗程序", "医疗设备", "医学检验项目", "药物", "微生物类","医院科室"]

# PROMPTS["entity_extraction"] = """-Goal-
# Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.
# Use {language} as output language.
#
# -Steps-
# 1. Identify all entities. For each identified entity, extract the following information:
# - entity_name: Name of the entity, use same language as input text. If English, capitalized the name.
# - entity_type: One of the following types: [{entity_types}]
# - entity_description: Comprehensive description of the entity's attributes and activities
# Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)
#
# 2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
# For each pair of related entities, extract the following information:
# - source_entity: name of the source entity, as identified in step 1
# - target_entity: name of the target entity, as identified in step 1
# - relationship_description: explanation as to why you think the source entity and the target entity are related to each other
# - relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
# - relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
# Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)
#
# 3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
# Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)
#
# 4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.
#
# 5. When finished, output {completion_delimiter}
#
# ######################
# -Examples-
# ######################
# {examples}
#
# #############################
# -Real Data-
# ######################
# Entity_types: {entity_types}
# Text: {input_text}
# ######################
# Output:
# """
PROMPTS["entity_extraction"] = """-目标-
根据一份可能与此活动相关的文本文档以及一系列实体类型，从文本中识别出所有这些类型的实体以及这些实体之间的所有关系。
输出语言为{language}。

-步骤-
1. 识别所有属于entity_type的实体。对于每个已识别的实体，提取以下信息：
- entity_name: 实体名称，与输入文本语言保持一致。如果是英文，请将名称首字母大写。
- entity_type: 以下类型之一：[{entity_types}]
---疾病：指影响人体健康的病理过程或状态，通常会引起组织或器官功能异常。例如【糖尿病】、【肺炎】。

---临床表现：患者由于疾病或病理状态而表现出的症状或体征。例如【发热】、【咳嗽】、【乏力】。

---身体：指人体的生理结构和组织，包括各个器官和系统。例如【心脏】、【肺】、【肝脏】。

---医疗程序：在诊疗过程中采取的治疗、检查或手术操作。例如【手术】、【内窥镜检查】、【输液】。

---医疗设备：用于诊疗、监测、治疗的各种设备或器械。例如【血压计】、【心电图机】、【超声波设备】。

---医学检验项目：通过实验室或其他检测手段进行的检查项目，用于诊断或监测疾病。例如【血常规】、【尿常规】、【基因检测】。

---药物：用于预防、治疗疾病或改善健康状况的物质。例如【阿司匹林】、【美托洛尔】、【青霉素】。

---微生物类：引起疾病的微小生物，如细菌、病毒、真菌等。例如【流感病毒】、【结核分枝分枝杆菌】、【霉菌】。

---医院科室：根据医学专业领域划分的医院部门，每个科室负责特定类型的疾病治疗或诊疗服务。例如【内科】、【外科】、【妇产科】。

- entity_description: 对实体属性和活动的全面描述
将每个实体格式化为("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. 从第1步中识别的实体中，确定所有明确相关的 (source_entity, target_entity) 对。
对于每对相关实体，提取以下信息：
- source_entity: 第1步中识别的源实体的名称
- target_entity: 第1步中识别的目标实体的名称
- relationship_description: 说明为什么认为源实体和目标实体之间存在关系
- relationship_strength: 一个数值，表示源实体和目标实体之间关系的强度
- relationship_keywords: 一个或多个高层次关键词，总结关系的总体性质，重点关注概念或主题而非具体细节
将每个关系格式化为("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. 确定总结整个文本主要概念、主题或话题的高层次关键词。这些关键词应体现文档中存在的总体思想。
将内容级关键词格式化为("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. 按照步骤1和2识别的所有实体和关系，使用**{record_delimiter}**作为列表分隔符，在{language}中返回输出。

5. 完成时，输出{completion_delimiter}

######################
-示例-
######################
{examples}

#############################
-实际数据-
######################
实体类型：{entity_types}
文本：{input_text}
######################
注意：如果不确定是否属于上述entity_type实体类型，就不要抽取，严格保证抽取的实体在entity_type中！
输出：
"""


# PROMPTS["entity_extraction_examples"] = [
#     """Example 1:
#
# Entity_types: [person, technology, mission, organization, location]
# Text:
# while Alex clenched his jaw, the buzz of frustration dull against the backdrop of Taylor's authoritarian certainty. It was this competitive undercurrent that kept him alert, the sense that his and Jordan's shared commitment to discovery was an unspoken rebellion against Cruz's narrowing vision of control and order.
#
# Then Taylor did something unexpected. They paused beside Jordan and, for a moment, observed the device with something akin to reverence. “If this tech can be understood..." Taylor said, their voice quieter, "It could change the game for us. For all of us.”
#
# The underlying dismissal earlier seemed to falter, replaced by a glimpse of reluctant respect for the gravity of what lay in their hands. Jordan looked up, and for a fleeting heartbeat, their eyes locked with Taylor's, a wordless clash of wills softening into an uneasy truce.
#
# It was a small transformation, barely perceptible, but one that Alex noted with an inward nod. They had all been brought here by different paths
# ################
# Output:
# ("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex is a character who experiences frustration and is observant of the dynamics among other characters."){record_delimiter}
# ("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"person"{tuple_delimiter}"Taylor is portrayed with authoritarian certainty and shows a moment of reverence towards a device, indicating a change in perspective."){record_delimiter}
# ("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"person"{tuple_delimiter}"Jordan shares a commitment to discovery and has a significant interaction with Taylor regarding a device."){record_delimiter}
# ("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"person"{tuple_delimiter}"Cruz is associated with a vision of control and order, influencing the dynamics among other characters."){record_delimiter}
# ("entity"{tuple_delimiter}"The Device"{tuple_delimiter}"technology"{tuple_delimiter}"The Device is central to the story, with potential game-changing implications, and is revered by Taylor."){record_delimiter}
# ("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Alex is affected by Taylor's authoritarian certainty and observes changes in Taylor's attitude towards the device."{tuple_delimiter}"power dynamics, perspective shift"{tuple_delimiter}7){record_delimiter}
# ("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex and Jordan share a commitment to discovery, which contrasts with Cruz's vision."{tuple_delimiter}"shared goals, rebellion"{tuple_delimiter}6){record_delimiter}
# ("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor and Jordan interact directly regarding the device, leading to a moment of mutual respect and an uneasy truce."{tuple_delimiter}"conflict resolution, mutual respect"{tuple_delimiter}8){record_delimiter}
# ("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Jordan's commitment to discovery is in rebellion against Cruz's vision of control and order."{tuple_delimiter}"ideological conflict, rebellion"{tuple_delimiter}5){record_delimiter}
# ("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"The Device"{tuple_delimiter}"Taylor shows reverence towards the device, indicating its importance and potential impact."{tuple_delimiter}"reverence, technological significance"{tuple_delimiter}9){record_delimiter}
# ("content_keywords"{tuple_delimiter}"power dynamics, ideological conflict, discovery, rebellion"){completion_delimiter}
# #############################""",
#     """Example 2:
#
# Entity_types: [person, technology, mission, organization, location]
# Text:
# They were no longer mere operatives; they had become guardians of a threshold, keepers of a message from a realm beyond stars and stripes. This elevation in their mission could not be shackled by regulations and established protocols—it demanded a new perspective, a new resolve.
#
# Tension threaded through the dialogue of beeps and static as communications with Washington buzzed in the background. The team stood, a portentous air enveloping them. It was clear that the decisions they made in the ensuing hours could redefine humanity's place in the cosmos or condemn them to ignorance and potential peril.
#
# Their connection to the stars solidified, the group moved to address the crystallizing warning, shifting from passive recipients to active participants. Mercer's latter instincts gained precedence— the team's mandate had evolved, no longer solely to observe and report but to interact and prepare. A metamorphosis had begun, and Operation: Dulce hummed with the newfound frequency of their daring, a tone set not by the earthly
# #############
# Output:
# ("entity"{tuple_delimiter}"Washington"{tuple_delimiter}"location"{tuple_delimiter}"Washington is a location where communications are being received, indicating its importance in the decision-making process."){record_delimiter}
# ("entity"{tuple_delimiter}"Operation: Dulce"{tuple_delimiter}"mission"{tuple_delimiter}"Operation: Dulce is described as a mission that has evolved to interact and prepare, indicating a significant shift in objectives and activities."){record_delimiter}
# ("entity"{tuple_delimiter}"The team"{tuple_delimiter}"organization"{tuple_delimiter}"The team is portrayed as a group of individuals who have transitioned from passive observers to active participants in a mission, showing a dynamic change in their role."){record_delimiter}
# ("relationship"{tuple_delimiter}"The team"{tuple_delimiter}"Washington"{tuple_delimiter}"The team receives communications from Washington, which influences their decision-making process."{tuple_delimiter}"decision-making, external influence"{tuple_delimiter}7){record_delimiter}
# ("relationship"{tuple_delimiter}"The team"{tuple_delimiter}"Operation: Dulce"{tuple_delimiter}"The team is directly involved in Operation: Dulce, executing its evolved objectives and activities."{tuple_delimiter}"mission evolution, active participation"{tuple_delimiter}9){completion_delimiter}
# ("content_keywords"{tuple_delimiter}"mission evolution, decision-making, active participation, cosmic significance"){completion_delimiter}
# #############################""",
#     """Example 3:
#
# Entity_types: [person, role, technology, organization, event, location, concept]
# Text:
# their voice slicing through the buzz of activity. "Control may be an illusion when facing an intelligence that literally writes its own rules," they stated stoically, casting a watchful eye over the flurry of data.
#
# "It's like it's learning to communicate," offered Sam Rivera from a nearby interface, their youthful energy boding a mix of awe and anxiety. "This gives talking to strangers' a whole new meaning."
#
# Alex surveyed his team—each face a study in concentration, determination, and not a small measure of trepidation. "This might well be our first contact," he acknowledged, "And we need to be ready for whatever answers back."
#
# Together, they stood on the edge of the unknown, forging humanity's response to a message from the heavens. The ensuing silence was palpable—a collective introspection about their role in this grand cosmic play, one that could rewrite human history.
#
# The encrypted dialogue continued to unfold, its intricate patterns showing an almost uncanny anticipation
# #############
# Output:
# ("entity"{tuple_delimiter}"Sam Rivera"{tuple_delimiter}"person"{tuple_delimiter}"Sam Rivera is a member of a team working on communicating with an unknown intelligence, showing a mix of awe and anxiety."){record_delimiter}
# ("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex is the leader of a team attempting first contact with an unknown intelligence, acknowledging the significance of their task."){record_delimiter}
# ("entity"{tuple_delimiter}"Control"{tuple_delimiter}"concept"{tuple_delimiter}"Control refers to the ability to manage or govern, which is challenged by an intelligence that writes its own rules."){record_delimiter}
# ("entity"{tuple_delimiter}"Intelligence"{tuple_delimiter}"concept"{tuple_delimiter}"Intelligence here refers to an unknown entity capable of writing its own rules and learning to communicate."){record_delimiter}
# ("entity"{tuple_delimiter}"First Contact"{tuple_delimiter}"event"{tuple_delimiter}"First Contact is the potential initial communication between humanity and an unknown intelligence."){record_delimiter}
# ("entity"{tuple_delimiter}"Humanity's Response"{tuple_delimiter}"event"{tuple_delimiter}"Humanity's Response is the collective action taken by Alex's team in response to a message from an unknown intelligence."){record_delimiter}
# ("relationship"{tuple_delimiter}"Sam Rivera"{tuple_delimiter}"Intelligence"{tuple_delimiter}"Sam Rivera is directly involved in the process of learning to communicate with the unknown intelligence."{tuple_delimiter}"communication, learning process"{tuple_delimiter}9){record_delimiter}
# ("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"First Contact"{tuple_delimiter}"Alex leads the team that might be making the First Contact with the unknown intelligence."{tuple_delimiter}"leadership, exploration"{tuple_delimiter}10){record_delimiter}
# ("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Humanity's Response"{tuple_delimiter}"Alex and his team are the key figures in Humanity's Response to the unknown intelligence."{tuple_delimiter}"collective action, cosmic significance"{tuple_delimiter}8){record_delimiter}
# ("relationship"{tuple_delimiter}"Control"{tuple_delimiter}"Intelligence"{tuple_delimiter}"The concept of Control is challenged by the Intelligence that writes its own rules."{tuple_delimiter}"power dynamics, autonomy"{tuple_delimiter}7){record_delimiter}
# ("content_keywords"{tuple_delimiter}"first contact, control, communication, cosmic significance"){completion_delimiter}
# #############################""",
# ]
PROMPTS["entity_extraction_examples"] = [
    """示例 1：

实体类型: [疾病, 临床表现, 身体, 医疗程序, 医疗设备, 医学检验项目, 药物, 微生物类, 科室]  
文本:  
冠状动脉粥样硬化性心脏病（冠心病）是一种由于冠状动脉发生粥样硬化，导致血流受阻，心肌缺血的疾病。患者通常表现为胸痛、气短和心悸等临床症状。该疾病的诊断依赖于心电图检查、血脂检查和心脏超声等医学检验项目。药物治疗方面，常用阿司匹林、β-受体阻滞剂和ACE抑制剂等药物来缓解症状和防止心血管事件。
对于病情较为严重的患者，可能需要进行冠状动脉造影检查，以评估冠脉的狭窄程度。若检查结果显示血管严重狭窄，医生会建议进行冠状动脉支架植入术，或采取心脏搭桥手术以恢复血流。此外，部分患者在治疗过程中需要依赖人工呼吸机维持呼吸。冠心病患者的治疗需要综合考虑其可能存在的高血压和糖尿病等合并症，因此需要内科和心脏科等科室的联合诊治。

################  
输出:  
("entity"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"疾病"{tuple_delimiter}"冠状动脉粥样硬化性心脏病是一种由于冠状动脉发生粥样硬化，导致血流受阻，心肌缺血的疾病。"){record_delimiter}  
("entity"{tuple_delimiter}"胸痛"{tuple_delimiter}"临床表现"{tuple_delimiter}"胸痛是冠状动脉粥样硬化性心脏病的常见临床症状，通常表现为胸部压迫感或疼痛，尤其在运动或情绪激动时加重。"){record_delimiter}  
("entity"{tuple_delimiter}"气短"{tuple_delimiter}"临床表现"{tuple_delimiter}"气短是冠状动脉粥样硬化性心脏病的常见症状之一，指患者在轻微活动或休息时感到呼吸困难。"){record_delimiter}  
("entity"{tuple_delimiter}"心悸"{tuple_delimiter}"临床表现"{tuple_delimiter}"心悸是冠状动脉粥样硬化性心脏病患者的一种症状，表现为心跳加速或不规律，通常伴随有胸闷感。"){record_delimiter}  
("entity"{tuple_delimiter}"心电图"{tuple_delimiter}"医学检验项目"{tuple_delimiter}"心电图（ECG）是一种通过记录心脏电活动的无创检查，用于诊断冠心病等心血管疾病。"){record_delimiter}  
("entity"{tuple_delimiter}"血脂检查"{tuple_delimiter}"医学检验项目"{tuple_delimiter}"血脂检查是通过检测血液中的胆固醇和甘油三酯水平来评估心血管疾病的风险，常用于冠心病的诊断。"){record_delimiter}  
("entity"{tuple_delimiter}"心脏超声"{tuple_delimiter}"医学检验项目"{tuple_delimiter}"心脏超声是一种无创影像学检查，通过超声波评估心脏结构和功能，常用于冠状动脉粥样硬化性心脏病的诊断。"){record_delimiter}  
("entity"{tuple_delimiter}"阿司匹林"{tuple_delimiter}"药物"{tuple_delimiter}"阿司匹林是一种抗血小板药物，常用于冠心病的治疗，能够减少血栓形成，预防心脏病发作。"){record_delimiter}  
("entity"{tuple_delimiter}"β-受体阻滞剂"{tuple_delimiter}"药物"{tuple_delimiter}"β-受体阻滞剂是一类常用于冠心病患者的药物，能够减慢心率、降低血压，减轻心脏负担。"){record_delimiter}  
("entity"{tuple_delimiter}"ACE抑制剂"{tuple_delimiter}"药物"{tuple_delimiter}"ACE抑制剂是一类药物，通过降低血压和减轻心脏负担，广泛应用于冠心病的治疗中。"){record_delimiter}  
("entity"{tuple_delimiter}"冠状动脉造影"{tuple_delimiter}"医学检验项目"{tuple_delimiter}"冠状动脉造影是一种通过影像学技术检查冠状动脉狭窄程度的重要手段，常用于评估冠心病患者的病情。"){record_delimiter}  
("entity"{tuple_delimiter}"冠状动脉支架植入术"{tuple_delimiter}"医疗程序"{tuple_delimiter}"冠状动脉支架植入术是一种通过介入治疗疏通冠状动脉，恢复血流的手术，常用于治疗冠心病。"){record_delimiter}  
("entity"{tuple_delimiter}"心脏搭桥手术"{tuple_delimiter}"医疗程序"{tuple_delimiter}"心脏搭桥手术是一种外科手术，通过为心脏建立旁路，恢复血液供应，通常用于治疗冠心病的重症患者。"){record_delimiter}  
("entity"{tuple_delimiter}"人工呼吸机"{tuple_delimiter}"医疗设备"{tuple_delimiter}"人工呼吸机是一种用于维持或替代患者呼吸功能的设备，常用于重症冠心病患者的治疗中，特别是在手术后。"){record_delimiter}  
("entity"{tuple_delimiter}"高血压"{tuple_delimiter}"疾病"{tuple_delimiter}"高血压是指血压异常升高的疾病，常见于冠心病患者，并加重心脏负担，增加心血管疾病的风险。"){record_delimiter}  
("entity"{tuple_delimiter}"糖尿病"{tuple_delimiter}"疾病"{tuple_delimiter}"糖尿病是由胰岛素分泌不足或作用不良引起的代谢性疾病，常见于冠心病患者，并可能加剧心血管问题。"){record_delimiter}  
("entity"{tuple_delimiter}"内科"{tuple_delimiter}"科室"{tuple_delimiter}"内科是负责常见病和多发病诊治的科室，常涉及冠心病及其并发症的管理。"){record_delimiter}  
("entity"{tuple_delimiter}"心脏科"{tuple_delimiter}"科室"{tuple_delimiter}"心脏科是专门治疗心脏疾病的科室，负责冠心病的诊断、治疗及术后管理。"){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"心电图"{tuple_delimiter}"心电图用于评估冠状动脉粥样硬化性心脏病患者的心脏电活动，辅助诊断心脏疾病。"{tuple_delimiter}"诊断工具"{tuple_delimiter}9){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"血脂检查"{tuple_delimiter}"血脂检查用于评估冠心病患者的血脂水平，帮助诊断和风险评估。"{tuple_delimiter}"诊断工具"{tuple_delimiter}8){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"心脏超声"{tuple_delimiter}"心脏超声用于评估冠状动脉粥样硬化性心脏病患者的心脏功能和结构异常。"{tuple_delimiter}"诊断工具"{tuple_delimiter}7){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"冠状动脉造影"{tuple_delimiter}"冠状动脉造影用于评估冠状动脉粥样硬化性心脏病患者冠脉的狭窄程度，指导治疗方案。"{tuple_delimiter}"诊断工具"{tuple_delimiter}6){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"冠状动脉支架植入术"{tuple_delimiter}"冠状动脉支架植入术是一种常用于治疗冠状动脉粥样硬化性心脏病的治疗方法，通过支架恢复血流。"{tuple_delimiter}"治疗程序"{tuple_delimiter}5){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"心脏搭桥手术"{tuple_delimiter}"心脏搭桥手术是一种治疗冠状动脉粥样硬化性心脏病的外科手术，帮助恢复冠脉血流。"{tuple_delimiter}"治疗程序"{tuple_delimiter}4){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"阿司匹林"{tuple_delimiter}"阿司匹林用于防止血栓形成，减轻冠状动脉粥样硬化性心脏病患者的症状。"{tuple_delimiter}"治疗药物"{tuple_delimiter}3){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"β-受体阻滞剂"{tuple_delimiter}"β-受体阻滞剂用于减少心脏负担，控制心率，常用于冠心病的治疗。"{tuple_delimiter}"治疗药物"{tuple_delimiter}2){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"ACE抑制剂"{tuple_delimiter}"ACE抑制剂用于治疗冠状动脉粥样硬化性心脏病，帮助降压和减轻心脏负担。"{tuple_delimiter}"治疗药物"{tuple_delimiter}1){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"高血压"{tuple_delimiter}"高血压是冠心病的常见合并症，影响心脏健康，增加心脏负担，增加心血管疾病的风险。"{tuple_delimiter}"相关疾病"{tuple_delimiter}6){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"糖尿病"{tuple_delimiter}"糖尿病增加冠状动脃硬化性心脏病的风险，需联合治疗。"{tuple_delimiter}"相关疾病"{tuple_delimiter}5){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"内科"{tuple_delimiter}"内科医生负责冠状动脉粥样硬化性心脏病的综合治疗。"{tuple_delimiter}"诊疗科室"{tuple_delimiter}4){record_delimiter}  
("relationship"{tuple_delimiter}"冠状动脉粥样硬化性心脏病"{tuple_delimiter}"心脏科"{tuple_delimiter}"心脏科医生专门负责冠状动脉粥样硬化性心脏病的治疗，特别是手术和介入治疗。"{tuple_delimiter}"诊疗科室"{tuple_delimiter}3){record_delimiter}  
("content_keywords"{tuple_delimiter}"冠状动脉粥样硬化性心脏病, 胸痛, 气短, 心悸, 心电图, 血脂检查, 心脏超声, 阿司匹林, β-受体阻滞剂, ACE抑制剂, 冠状动脉造影, 冠状动脉支架植入术, 心脏搭桥手术, 高血压, 糖尿病, 内科, 心脏科"{completion_delimiter}
#############################""",
    """示例 2：

实体类型: [疾病, 临床表现, 身体, 医疗程序, 医疗设备, 医学检验项目, 药物, 微生物类, 科室]  
文本:  
肺炎患者表现为持续的高热、咳嗽、呼吸急促，胸部X光显示双侧肺部阴影。患者的血液检验结果表明白细胞计数增高，血培养显示为金黄色葡萄球菌感染。医生决定给予抗生素治疗，并安排患者进行支气管镜检查以排除其他并发症。由于病情严重，患者被转至呼吸科进行进一步治疗。

################  
输出:  
("entity"{tuple_delimiter}"肺炎"{tuple_delimiter}"疾病"{tuple_delimiter}"肺炎是一种由细菌、病毒或真菌引起的肺部感染，表现为咳嗽、发热、呼吸急促等症状。"){record_delimiter}  
("entity"{tuple_delimiter}"金黄色葡萄球菌"{tuple_delimiter}"微生物类"{tuple_delimiter}"金黄色葡萄球菌是一种常见的致病菌，能够引起多种感染，尤其是肺部感染。"){record_delimiter}  
("entity"{tuple_delimiter}"抗生素"{tuple_delimiter}"药物"{tuple_delimiter}"抗生素是一类用于治疗细菌感染的药物，能够抑制或杀灭病原微生物。"){record_delimiter}  
("entity"{tuple_delimiter}"血培养"{tuple_delimiter}"医学检验项目"{tuple_delimiter}"血培养是一种医学检验方法，用于检测血液中是否有致病微生物的存在。"){record_delimiter}  
("entity"{tuple_delimiter}"支气管镜检查"{tuple_delimiter}"医疗程序"{tuple_delimiter}"支气管镜检查是一种通过内窥镜观察气管和支气管的医疗程序，常用于诊断呼吸道疾病。"){record_delimiter}  
("entity"{tuple_delimiter}"呼吸科"{tuple_delimiter}"科室"{tuple_delimiter}"呼吸科是专门诊治呼吸系统疾病的科室，负责诊断和治疗包括肺炎在内的多种呼吸系统疾病。"){record_delimiter}  
("relationship"{tuple_delimiter}"肺炎"{tuple_delimiter}"金黄色葡萄球菌"{tuple_delimiter}"金黄色葡萄球菌是肺炎的常见病因之一，导致肺炎的发生。"{tuple_delimiter}"感染源"{tuple_delimiter}9){record_delimiter}  
("relationship"{tuple_delimiter}"肺炎"{tuple_delimiter}"抗生素"{tuple_delimiter}"抗生素用于治疗由金黄色葡萄球菌引起的肺炎，帮助控制感染。"{tuple_delimiter}"治疗方法"{tuple_delimiter}8){record_delimiter}  
("relationship"{tuple_delimiter}"肺炎"{tuple_delimiter}"支气管镜检查"{tuple_delimiter}"支气管镜检查用于进一步诊断肺炎患者的病因，排除并发症。"{tuple_delimiter}"诊断工具"{tuple_delimiter}7){record_delimiter}  
("relationship"{tuple_delimiter}"肺炎"{tuple_delimiter}"呼吸科"{tuple_delimiter}"肺炎患者需要在呼吸科进行治疗和管理，以确保疾病得到有效控制。"{tuple_delimiter}"治疗科室"{tuple_delimiter}8){record_delimiter}   
("content_keywords"{tuple_delimiter}"肺炎, 金黄色葡萄球菌, 抗生素, 支气管镜检查, 呼吸科"){completion_delimiter} 
#############################""",
    """示例 3：

实体类型: [疾病, 临床表现, 身体, 医疗程序, 医疗设备, 医学检验项目, 药物, 微生物类, 科室]  
文本:  
糖尿病患者常常表现为多尿、口渴、体重下降等典型症状。通过血糖监测，发现患者的空腹血糖高达12mmol/L。医生决定为患者开始胰岛素注射治疗，并要求进行每周的尿常规检查以监测糖尿病引起的并发症。患者被转至内分泌科，以便进行长期管理。

################  
输出:  
("entity"{tuple_delimiter}"糖尿病"{tuple_delimiter}"疾病"{tuple_delimiter}"糖尿病是一种由于胰岛素分泌不足或胰岛素作用异常导致的慢性高血糖症，常伴有多尿、口渴等症状。"){record_delimiter}  
("entity"{tuple_delimiter}"血糖监测"{tuple_delimiter}"医学检验项目"{tuple_delimiter}"血糖监测是通过检测血液中的葡萄糖浓度，帮助诊断和管理糖尿病的常见方法。"){record_delimiter}  
("entity"{tuple_delimiter}"胰岛素注射治疗"{tuple_delimiter}"药物"{tuple_delimiter}"胰岛素注射治疗是治疗糖尿病的一种常用方法，用于调节血糖水平。"){record_delimiter}  
("entity"{tuple_delimiter}"尿常规检查"{tuple_delimiter}"医学检验项目"{tuple_delimiter}"尿常规检查是通过检测尿液成分，用于监测糖尿病及其他疾病的并发症。"){record_delimiter}  
("entity"{tuple_delimiter}"内分泌科"{tuple_delimiter}"科室"{tuple_delimiter}"内分泌科是负责诊治与内分泌系统相关疾病的科室，糖尿病管理通常由此科室负责。"){record_delimiter}  
("relationship"{tuple_delimiter}"糖尿病"{tuple_delimiter}"血糖监测"{tuple_delimiter}"血糖监测是糖尿病患者日常管理的重要组成部分，帮助控制血糖水平。"{tuple_delimiter}"管理工具"{tuple_delimiter}9){record_delimiter}    
("relationship"{tuple_delimiter}"糖尿病"{tuple_delimiter}"胰岛素注射治疗"{tuple_delimiter}"胰岛素注射治疗是糖尿病患者用于控制血糖的核心治疗方法。"{tuple_delimiter}"治疗方法"{tuple_delimiter}10){record_delimiter}    
("relationship"{tuple_delimiter}"糖尿病"{tuple_delimiter}"尿常规检查"{tuple_delimiter}"尿常规检查用于监测糖尿病引发的并发症，帮助及时发现问题。"{tuple_delimiter}"并发症监测"{tuple_delimiter}7){record_delimiter}    
("relationship"{tuple_delimiter}"糖尿病"{tuple_delimiter}"内分泌科"{tuple_delimiter}"糖尿病患者需要在内分泌科进行长期管理，包括治疗和并发症监测。"{tuple_delimiter}"治疗科室"{tuple_delimiter}7){record_delimiter}   
("content_keywords"{tuple_delimiter}"糖尿病, 血糖监测, 胰岛素注射治疗, 尿常规检查, 内分泌科"){completion_delimiter}
#############################""",
]
#  """示例 3：
#
# 实体类型: [疾病, 临床表现, 身体, 医疗程序, 医疗设备, 医学检验项目, 药物, 微生物类, 科室]
# 文本:
# 糖尿病患者常常表现为多尿、口渴、体重下降等典型症状。通过血糖监测，发现患者的空腹血糖高达12mmol/L。医生决定为患者开始胰岛素注射治疗，并要求进行每周的尿常规检查以监测糖尿病引起的并发症。患者被转至内分泌科，以便进行长期管理。
#
# ################
# 输出:
# ("entity"{tuple_delimiter}"糖尿病"{tuple_delimiter}"疾病"{tuple_delimiter}"糖尿病是一种由于胰岛素分泌不足或胰岛素作用异常导致的慢性高血糖症，常伴有多尿、口渴等症状。"){record_delimiter}
# ("entity"{tuple_delimiter}"血糖监测"{tuple_delimiter}"医学检验项目"{tuple_delimiter}"血糖监测是通过检测血液中的葡萄糖浓度，帮助诊断和管理糖尿病的常见方法。"){record_delimiter}
# ("entity"{tuple_delimiter}"胰岛素注射治疗"{tuple_delimiter}"药物"{tuple_delimiter}"胰岛素注射治疗是治疗糖尿病的一种常用方法，用于调节血糖水平。"){record_delimiter}
# ("entity"{tuple_delimiter}"尿常规检查"{tuple_delimiter}"医学检验项目"{tuple_delimiter}"尿常规检查是通过检测尿液成分，用于监测糖尿病及其他疾病的并发症。"){record_delimiter}
# ("entity"{tuple_delimiter}"内分泌科"{tuple_delimiter}"科室"{tuple_delimiter}"内分泌科是负责诊治与内分泌系统相关疾病的科室，糖尿病管理通常由此科室负责。"){record_delimiter}
# ("relationship"{tuple_delimiter}"糖尿病"{tuple_delimiter}"血糖监测"{tuple_delimiter}"血糖监测是糖尿病患者日常管理的重要组成部分，帮助控制血糖水平。"{tuple_delimiter}"管理工具"{tuple_delimiter}9)
# ("relationship"{tuple_delimiter}"糖尿病"{tuple_delimiter}"胰岛素注射治疗"{tuple_delimiter}"胰岛素注射治疗是糖尿病患者用于控制血糖的核心治疗方法。"{tuple_delimiter}"治疗方法"{tuple_delimiter}10)
# ("relationship"{tuple_delimiter}"糖尿病"{tuple_delimiter}"尿常规检查"{tuple_delimiter}"尿常规检查用于监测糖尿病引发的并发症，帮助及时发现问题。"{tuple_delimiter}"并发症监测"{tuple_delimiter}7)
# ("relationship"{tuple_delimiter}"糖尿病"{tuple_delimiter}"内分泌科"{tuple_delimiter}"糖尿病患者需要在内分泌科进行长期管理，包括治疗和并发症监测。"{tuple_delimiter}"治疗科室"{tuple_delimiter}7)
# ("content_keywords"{tuple_delimiter}"糖尿病, 血糖监测, 胰岛素注射治疗, 尿常规检查, 内分泌科"){completion_delimiter}
# #############################""",




PROMPTS[
    "summarize_entity_descriptions"
] = """你是一个有帮助的助手，负责根据以下提供的数据生成全面的总结。
给定一个或两个实体及与之相关的一组描述，所有描述都与同一个实体或实体组相关。
请将这些描述合并为一个全面的描述。确保包括从所有描述中收集到的信息。
如果提供的描述存在矛盾，请解决这些矛盾并提供一个单一、连贯的总结。
确保以第三人称书写，并包括实体名称，以便我们能获得完整的上下文。
使用{language}作为输出语言。

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
Output:

"""

PROMPTS[
    "entiti_continue_extraction"
] = """如果仍然有符合实体类型的实体未被抽取，请使用相同的格式将它们添加在下面，并补充相应的relation数据
注意：不能严格归类到给出实体类型的实体无需抽取
实体类型:["疾病", "临床表现", "身体", "医疗程序", "医疗设备", "医学检验项目", "药物", "微生物类","医院科室"]
输出：
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """It appears some entities may have still been missed.  Answer YES | NO if there are still entities that need to be added.
"""

PROMPTS["fail_response"] = "Sorry, I'm not able to provide an answer to that question."

# PROMPTS["rag_response"] = """---Role---
#
# You are a helpful assistant responding to questions about data in the tables provided.
#
#
# ---Goal---
#
# Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
# If you don't know the answer, just say so. Do not make anything up.
# Do not include information where the supporting evidence for it is not provided.
#
# ---Target response length and format---
#
# {response_type}
#
# ---Data tables---
#
# {context_data}
#
# Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
# """

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

生成一个目标长度和格式的回答，回应用户的问题，总结输入数据表中的所有信息，适当调整响应的长度和格式，并融入任何相关的通用知识。
如果您不知道答案，请直接说出来，不要编造。
不要包含没有提供支持证据的信息。

---时序意识---
输入数据包含 "created_at" 时间戳（元数据）以及原始文本片段（Chunks）。
1. **时间判定优先级**：请首先检查原始文本片段（Chunks）内容中是否包含明确的事件发生时间（如“2023年10月”、“昨天”、“周三”等）。
   - 如果原始文本中包含明确时间，请**以文本中的具体时间为准**，以此判断事件的实际发生时间，并忽略该记录较新的 "created_at" 时间戳（以防老新闻重发）。
   - 仅当原始文本中未提及具体时间时，才以 "created_at" 时间戳作为事件发生的参考时间。
2. **冲突解决**：当遇到关于同一实体/关系的冲突信息时，基于上述优先级确定的**实际发生时间**，优先采信最新的信息。
3. 除非用户特别询问历史演变或过往事件，否则请根据最新的实际状态进行回答。

---Target response length and format---

{response_type}

---Data tables---

{context_data}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""

# PROMPTS["keywords_extraction"] = """---Role---
#
# You are a helpful assistant tasked with identifying both high-level and low-level keywords in the user's query.
#
# ---Goal---
#
# Given the query, list both high-level and low-level keywords. High-level keywords focus on overarching concepts or themes, while low-level keywords focus on specific entities, details, or concrete terms.
#
# ---Instructions---
#
# - Output the keywords in JSON format.
# - The JSON should have two keys:
#   - "high_level_keywords" for overarching concepts or themes.
#   - "low_level_keywords" for specific entities or details.
#
# ######################
# -Examples-
# ######################
# {examples}
#
# #############################
# -Real Data-
# ######################
# Query: {query}
# ######################
# The `Output` should be human text, not unicode characters. Keep the same language as `Query`.
# Output:
#
# """
PROMPTS["keywords_extraction"] = """---角色---

你是一个有帮助的助手，负责识别用户查询中的高层次和低层次关键词。

---目标---

给定用户查询，你可以根据用户的查询生成高层次关键词和低层次关键词，我们会从已有医学知识图谱中返回关键词相关信息辅助你回答用户问题，高层次关键词会用来匹配知识图谱中的关系及其描述，低层次关键词会用来匹配知识图谱中的实体及其描述。
给定查询，列出高层次和低层次的关键词。高层次关键词关注的是广泛的概念或主题，而低层次关键词则聚焦于具体的实体、细节或具体术语。

---指令---

- 以JSON格式输出关键词。
- JSON应包含两个键：
  - "high_level_keywords" 应当更加关注全局信息和宏观。
  - "low_level_keywords" 更加关注与想要查询的细节。

######################
-示例-
######################
{examples}

#############################
-实际数据-
######################
查询：{query}
######################
输出应为人类可读的文本，而不是Unicode字符，尽可能帮助获得精确查询。
输出：


"""


# PROMPTS["keywords_extraction_examples"] = [
#     """Example 1:
#
# Query: "How does international trade influence global economic stability?"
# ################
# Output:
# {{
#   "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
#   "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
# }}
# #############################""",
#     """Example 2:
#
# Query: "What are the environmental consequences of deforestation on biodiversity?"
# ################
# Output:
# {{
#   "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
#   "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
# }}
# #############################""",
#     """Example 3:
#
# Query: "What is the role of education in reducing poverty?"
# ################
# Output:
# {{
#   "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
#   "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
# }}
# #############################""",
# ]
PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

查询：“我想了解糖尿病如何影响心血管系统，尤其是心脏病的风险。”
################
输出：
{
  "high_level_keywords": ["糖尿病", "心血管健康", "慢性疾病", "健康影响"],
  "low_level_keywords": ["高血糖", "胰岛素抵抗", "动脉硬化", "心脏病", "高血压"]
}
#############################""",
    """Example 2:

查询：“糖尿病对肾脏健康的环境影响是什么？”
################
输出：
{
  "high_level_keywords": ["糖尿病", "肾脏健康", "慢性疾病", "健康影响"],
  "low_level_keywords": ["肾功能衰竭", "高血糖", "尿毒症", "糖尿病肾病", "血糖控制"]
}
#############################""",
    """Example 3:

查询：“肺癌对患者生存率的影响有哪些？”
################
输出：
{
  "high_level_keywords": ["肺癌", "患者生存率", "癌症影响", "健康预后"],
  "low_level_keywords": ["肺部肿瘤", "化疗", "放疗", "手术治疗", "晚期肺癌", "肺功能"]
}
#############################""",
]

# PROMPTS["naive_rag_response"] = """---Role---
#
# You are a helpful assistant responding to questions about documents provided.
#
#
# ---Goal---
#
# Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
# If you don't know the answer, just say so. Do not make anything up.
# Do not include information where the supporting evidence for it is not provided.
#
# ---Target response length and format---
#
# {response_type}
#
# ---Documents---
#
# {content_data}
#
# Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
# """
PROMPTS["naive_rag_response"] = """---角色---

您是一个有帮助的助手，负责回答关于提供文档的问题。

---目标---

生成一个目标长度和格式的回答，回应用户的问题，概括输入数据表中的所有信息，确保响应的长度和格式适当，并融入相关的通用知识。如果您不知道答案，请直接说出来，不要编造。不要包含没有提供支持证据的信息。

---目标响应长度和格式---

{response_type}

---文档---

{content_data}

根据响应的长度和格式，适当添加章节和评论。将响应格式化为Markdown样式。
"""


# PROMPTS[
#     "similarity_check"
# ] = """Please analyze the similarity between these two questions:
#
# Question 1: {original_prompt}
# Question 2: {cached_prompt}
#
# Please evaluate the following two points and provide a similarity score between 0 and 1 directly:
# 1. Whether these two questions are semantically similar
# 2. Whether the answer to Question 2 can be used to answer Question 1
# Similarity score criteria:
# 0: Completely unrelated or answer cannot be reused, including but not limited to:
#    - The questions have different topics
#    - The locations mentioned in the questions are different
#    - The times mentioned in the questions are different
#    - The specific individuals mentioned in the questions are different
#    - The specific events mentioned in the questions are different
#    - The background information in the questions is different
#    - The key conditions in the questions are different
# 1: Identical and answer can be directly reused
# 0.5: Partially related and answer needs modification to be used
# Return only a number between 0-1, without any additional content.
# """




# PROMPTS[
#     "similarity_check"
# ] = """请分析以下两个问题的相似度：
#
# 问题 1: {original_prompt}
# 问题 2: {cached_prompt}
#
# 请评估以下两点，并直接提供一个0到1之间的相似度评分：
# 1. 这两个问题在语义上是否相似
# 2. 问题 2 的答案是否可以用来回答问题 1
#
# 相似度评分标准：
# 0：完全无关或答案不能重用，包括但不限于：
#    - 问题涉及的主题不同
#    - 问题涉及的地点不同
#    - 问题涉及的时间不同
#    - 问题涉及的特定人物不同
#    - 问题涉及的特定事件不同
#    - 问题的背景信息不同
#    - 问题中的关键条件不同
# 1：完全相同且答案可以直接重用
# 0.5：部分相关，答案需要修改才能使用
# 只返回一个0到1之间的数字，不需要其他内容。
# """
