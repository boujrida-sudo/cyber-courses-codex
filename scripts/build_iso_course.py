"""Build original learning material and a portable CyberAcademy XML package."""
import base64
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from course_xml import serialize_package, slugify
ROOT=Path(__file__).resolve().parents[1]
SOURCES={
 'community':('ISO27001security.com — supplementary ISMS guidance (user-supplied)','https://www.iso27001security.com/'),
 'iso':('ISO/IEC 27001:2022 — official standard overview','https://www.iso.org/standard/27001'),
 'climate':('ISO management system climate-action amendments','https://www.iso.org/climate-change/amendment'),
 'controls':('ISO/IEC 27002:2022 — control guidance','https://www.iso.org/standard/75652.html'),
 'transition':('IAF MD 26, Issue 2 — transition requirements for ISO/IEC 27001:2022','https://iaf.nu/wp-content/uploads/2023/02/IAF_MD_26_Issue_2_14022023.pdf'),
 'csf':('NIST Cybersecurity Framework — supporting risk-management guidance','https://www.nist.gov/cyberframework'),
 'risk':('NIST SP 800-30 Rev. 1 — Guide for Conducting Risk Assessments','https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf'),
 'incident':('NIST SP 800-61 Rev. 3 (2025) — Incident Response Recommendations','https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf'),
}
# Each quiz has one correct answer. Explanations are original summaries.
def q(prompt,answers,explanation):return {'prompt':prompt,'options':[{'text':a,'correct':i==0} for i,a in enumerate(answers)],'explanation':explanation}
DATA=[
('What an ISMS is and which edition applies',60,
'''An information security management system (ISMS) is a repeatable way to decide what information needs protection, manage the associated risks, and demonstrate that decisions are implemented and reviewed. Confidentiality prevents unauthorized disclosure; integrity protects accuracy and completeness; availability supports timely access. A management system connects people, processes, technology, leadership and evidence rather than purchasing a single security product.

The course baseline is ISO/IEC 27001:2022, the third edition, together with Amendment 1:2024 concerning climate action. There is no ISO/IEC 27001:2025 edition asserted in this course. The important 2025 change was the end of the transition period for accredited certification from the 2013 edition to the 2022 edition, on 31 October 2025 under IAF MD 26. That is a certification-transition date, not a new publication year.

Clauses 4–10 describe the management system requirements. Annex A supplies a reference set of controls used in risk treatment. ISO/IEC 27002:2022 provides implementation guidance and is not itself the ISMS certification requirements standard. Buying or reading the licensed standards is necessary when implementing exact requirements; these lessons use original explanations rather than reproducing their text.

Example: a training company protects learner records, examination questions and course availability. A backup addresses availability, but the ISMS also assigns an owner, sets recovery objectives, tests restoration, and reviews evidence. Course completion is introductory education and does not confer ISO certification.''',
'''Scenario: Cedar Learning is a fictional 25-person training provider with a cloud LMS, remote instructors and outsourced payments. Use synthetic information only.
1. List six information assets and their owners.
2. For each asset, describe one confidentiality, integrity and availability failure.
3. Choose the three most consequential failures and explain the business impact.
4. Write a 100-word statement explaining how an ISMS differs from a list of tools.
Deliverable: asset/CIA worksheet and the statement. Acceptance: named owners, concrete impacts and at least one example for each CIA property.''',
['iso','controls','transition'],[
q('Which baseline does this course use?',['ISO/IEC 27001:2022 plus Amendment 1:2024','ISO/IEC 27001:2025','ISO/IEC 27002 certification','Only ISO/IEC 27001:2013'],'The 2025 transition does not create a 2025 edition.'),
q('What does the 31 October 2025 milestone concern?',['Completion of the accredited 2013-to-2022 certification transition','Publication of a 2025 standard','A universal breach-reporting deadline','Mandatory use of one security product'],'IAF MD 26 governs the certification transition; contractual and legal deadlines are separate.'),
q('Which activity best demonstrates an ISMS?',['An owned risk process with implementation evidence and review','Purchasing a firewall only','A one-time vulnerability scan','An unsigned policy template'],'The management system connects decisions, responsibilities, evidence and continual improvement.')]),
('Organizational context, scope and the climate amendment',75,
'''Clause 4 starts by understanding the organization and its relevant internal and external issues, the interested parties and their relevant requirements, and the ISMS scope. Scope should identify business activities, locations, information, systems and important interfaces. A boundary that hides a critical outsourced service makes risk decisions unreliable even if the service is not directly operated by the organization.

Amendment 1:2024 adds climate-change considerations to management-system context. Organizations determine whether climate change is a relevant issue; the amendment also notes that relevant interested parties can have climate-related requirements. This is not a blanket instruction to implement environmental controls or certify an environmental management system. Document the assessment and its reasoning. If climate-related conditions affect information security, carry those conditions into risk assessment, continuity and supplier decisions as appropriate.

For Cedar Learning, prolonged heat or flooding could affect power, internet access or a hosting provider. Customers might require evidence of resilience during severe weather. An organization could also conclude that a particular climate issue is not relevant, provided the conclusion is supported and revisited when conditions change. Avoid treating a checkbox as sufficient analysis.

Keep a context register with issue, interested party, requirement, relevance, owner and review trigger. Review the scope after new services, new locations, acquisitions, supplier changes or significant incidents.''',
'''1. Write a one-paragraph scope for Cedar Learning covering the LMS, learner records, staff endpoints and hosting/payment interfaces.
2. Identify five interested parties and their requirements; distinguish actual requirements from assumptions to verify.
3. Assess heat, flooding and supplier resilience for information-security relevance.
4. Record one relevant and one currently non-relevant climate issue with reasons and review triggers.
5. Draw a simple boundary diagram and identify two dependencies outside direct control.
Deliverable: scope statement, context register and climate relevance record. Acceptance: explicit boundaries, justified relevance conclusions, and assigned review owners.''',
['iso','climate'],[
q('What does Amendment 1:2024 require organizations to consider?',['Whether climate change is a relevant issue in their context','Mandatory purchase of carbon offsets','An automatic new environmental certification','Elimination of all cloud services'],'Climate relevance is considered in organizational context; information-security implications follow where relevant.'),
q('Which scope description is strongest?',['Named activities, systems, locations and external interfaces','All security everywhere','Only the easiest server to audit','A supplier marketing slogan'],'An intelligible boundary enables risk assessment and reliable audit coverage.'),
q('What should a non-relevance conclusion contain?',['Reasoning and conditions that would trigger reassessment','Nothing beyond an unchecked box','A claim that weather never matters','A copy of another company’s scope'],'Context decisions should be defensible and reviewed as circumstances change.')]),
('Leadership, policy and accountable roles',60,
'''Clause 5 concerns leadership and commitment, information-security policy, and assigned responsibilities and authorities. Top management connects the ISMS with business direction, makes resources available and establishes accountability. Delegating implementation to an ISMS manager does not eliminate management responsibility.

A useful policy states the organization’s security intent, supports appropriate objectives, and commits to applicable requirements and continual improvement. Supporting standards and procedures explain concrete implementation. A policy should be approved, communicated and reviewed; employees need to understand how it affects their work.

Assign responsibility for risk decisions, access approvals, incident coordination, supplier oversight and internal audits. Different responsibilities may belong to different people. A RACI matrix is a helpful tool, not a prescribed format. Separate conflicting duties where practical; a small organization can use independent review as a compensating safeguard.

For Cedar Learning, the director approves the policy and resources, service owners own business risks, IT implements controls, and an independent reviewer evaluates audit evidence. Document escalation and who can accept residual risk. A course author should not unilaterally accept exposure of all learner records.''',
'''1. Draft a 250-word information-security policy for Cedar Learning.
2. Create a RACI for risk assessment, access approval, incident handling, supplier reviews and internal audit.
3. Identify one conflict of duties and propose an independent review.
4. Write a management approval record with owner, review date and communication method.
Deliverable: policy, RACI and approval record. Acceptance: visible management accountability and explicit residual-risk acceptance authority.''',
['iso','csf'],[
q('Who retains accountability for ISMS leadership?',['Top management','Only the firewall vendor','Only the auditor','Every supplier equally'],'Operational delegation does not remove leadership responsibilities.'),
q('Which item belongs in an effective security policy?',['Commitment to applicable requirements and continual improvement','Every employee password','Unapproved technical defaults only','A promise that no incident can happen'],'A policy communicates intent and commitments without exposing credentials or making impossible guarantees.'),
q('Why define residual-risk acceptance authority?',['So a responsible authorized owner approves remaining exposure','To let anyone waive security requirements','To eliminate audit evidence','To make all risks disappear'],'Acceptance is an accountable business decision and should follow established criteria.')]),
('Risk assessment and security objectives',90,
'''Clause 6 connects planning to information-security risk assessment, risk treatment and measurable objectives. Establish and maintain risk criteria so repeated assessments can be compared. Define likelihood, consequence, acceptance thresholds and how risk owners are identified. A 1–5 matrix is a teaching example, not an ISO-mandated scoring formula.

Describe risk as a plausible event affecting information and a business outcome: unauthorized use of an instructor account could expose learner records and disrupt teaching. Record asset/process, threat, vulnerability, existing controls, consequences, likelihood, score, owner and treatment decision. Distinguish current risk from residual risk expected after treatment.

NIST SP 800-30 provides supporting risk-assessment guidance, but its method does not replace ISO/IEC 27001 requirements. Consider uncertainty and evidence rather than assigning confident numbers without explanation. Risk assessment should be repeated at planned intervals and when significant changes occur.

Security objectives should state an intended outcome, a measure, an owner, a timeframe and how progress will be evaluated. For example, privileged LMS access reviews completed by their quarterly due date, with exceptions tracked to closure. A metric should drive a decision; counting documents alone rarely demonstrates effectiveness.''',
'''1. Define likelihood and impact scales from 1 to 5 and an acceptance threshold for this exercise.
2. Assess five scenarios: stolen administrator account, accidental grade modification, backup failure, unavailable hosting and supplier data exposure.
3. Record rationale, existing controls and an owner for each risk.
4. Choose two unacceptable risks and propose treatment plus expected residual risk.
5. Define three objectives with measure, target, owner and due date.
Deliverable: risk register and objectives tracker. Acceptance: reproducible criteria, reasoned scores and traceable ownership. The teaching scale is not a claim of an ISO-required method.''',
['iso','risk','csf'],[
q('Why establish risk criteria before scoring?',['To make assessments consistent and comparable','Because ISO mandates a single 5×5 matrix','To avoid assigning owners','To guarantee a zero-risk result'],'Organizations define suitable criteria; a particular scoring matrix is not prescribed.'),
q('Which statement is a useful risk description?',['Compromised instructor access could disclose learner records','Security is bad','Install antivirus','The risk score is five'],'A risk statement relates an event to information-security and business consequences.'),
q('Which objective is measurable?',['Review all privileged LMS accounts quarterly and track overdue exceptions','Improve everything eventually','Buy more tools','Never have any problems'],'A defined outcome, measure, timeframe and owner support evaluation.')]),
('Risk treatment, Annex A and the Statement of Applicability',90,
'''Risk treatment selects actions appropriate to assessed risks, such as changing the activity, implementing safeguards, sharing aspects of risk or accepting risk within defined criteria. Determine the controls necessary for treatment and compare them against Annex A to check that necessary controls have not been overlooked. Annex A is not a shortcut that replaces risk analysis.

The 2022 reference set contains 93 controls across organizational (37), people (8), physical (14) and technological (34) themes. ISO/IEC 27002:2022 supplies guidance. Eleven controls were introduced relative to the previous reference set, including threat intelligence, cloud-service security, ICT readiness for business continuity, physical security monitoring, configuration management, information deletion, data masking, data leakage prevention, monitoring activities, web filtering and secure coding. A changed control count does not imply reduced security work.

The Statement of Applicability (SoA) records necessary controls, justification for their inclusion, whether they are implemented, and justification for excluding Annex A controls. Controls needed for legal, contractual or business reasons may extend beyond Annex A. Document why a control is relevant, how it is implemented, and where evidence can be found; do not simply mark every line 'yes'.

A treatment plan records actions, owners, resources and dates. Risk owners approve the plan and accept residual risk. Keep the risk register, SoA and implementation evidence mutually consistent. Obtain the licensed standard for exact control identifiers and text; this course does not reproduce that material.''',
'''1. Use your lesson 4 risks to identify eight candidate safeguards across the four themes.
2. Create an SoA-style worksheet: control reference/topic, source risk or requirement, inclusion/exclusion reason, implementation status, owner and evidence.
3. Address cloud security, configuration management and ICT readiness explicitly.
4. Build a treatment plan for three gaps with dates and acceptance evidence.
5. Record an owner’s residual-risk decision and its rationale.
Deliverable: sample SoA, treatment plan and acceptance record. Acceptance: justified selections and exclusions, risks linked to controls, and no unsupported claims of full standard compliance.''',
['iso','controls'],[
q('How many controls are in the 2022 Annex A reference set?',['93','114','11','27001'],'There are 93 controls organized into four themes; 11 were introduced relative to the previous reference set.'),
q('What is the role of Annex A in treatment?',['A reference set used to check that necessary controls were not overlooked','A substitute for assessing risks','A list that must all be excluded','An automatic certificate'],'Necessary controls are determined through treatment and checked against Annex A.'),
q('What should the SoA explain?',['Control selection, implementation status and justified Annex A exclusions','Only a list of product names','Only an overall score','Passwords for every system'],'An SoA makes applicability decisions transparent and traceable.')]),
('People, competence and controlled documentation',60,
'''Clause 7 addresses resources, competence, awareness, communication and documented information. People need competence for assigned work, with suitable evidence such as experience, training and demonstrated performance. Attendance at a presentation alone does not establish competence.

Awareness should help people understand policy, their contribution to ISMS effectiveness and the consequences of failing to follow requirements. For a training provider, practical examples include identifying phishing, using approved sharing methods, and promptly reporting suspected exposure of learner records. Communication planning considers what to communicate, when, to whom, by whom and how.

Documented information must be identifiable, reviewed and approved as appropriate, available where needed and protected against inappropriate changes or disclosure. Manage access, versions, retention and disposal. Evidence includes both maintained documents, such as a procedure, and retained records, such as an access-review result.

Avoid a paperwork-only system. A concise procedure used by staff is more valuable than a large copied manual nobody follows. Associate each important document with an owner and review trigger, and each record with a retention rule grounded in actual business and legal requirements.''',
'''1. Define competence requirements for the LMS administrator, incident coordinator and instructor.
2. Design a 15-minute awareness exercise with a scenario and observable success criteria.
3. Create a document register: identifier, owner, approval, current version, access and review date.
4. Create a records schedule for risk reviews, training evidence and access approvals; mark retention periods as proposals requiring legal/business confirmation.
5. Demonstrate a procedure update with an approval and change log.
Deliverable: competence matrix, awareness exercise and document/records registers. Acceptance: evidence of competence beyond attendance and clear version/access controls.''',
['iso','controls','csf'],[
q('Which evidence best supports competence?',['A successful observed task against defined criteria','Attendance alone in every situation','An unopened handbook','A job title alone'],'Competence concerns ability to perform assigned work; suitable evidence depends on the role.'),
q('Why control document versions?',['To keep approved information available and prevent use of obsolete instructions','To prevent all revisions','To publish confidential records','To avoid ownership'],'Version and approval controls help staff use current instructions.'),
q('What is a retained record?',['Evidence that an access review was completed','A draft plan with no approval','A general slogan','A hypothetical future task'],'Records show performed activities and results.')]),
('Operating controls, suppliers and incident response',90,
'''Clause 8 concerns operational planning and control, performing risk assessments and implementing treatment. Convert decisions into routines: access approvals and removals, configuration baselines, supplier reviews, change assessments and incident handling. Define criteria and retain enough evidence to show operations followed the plan.

Cloud-service security requires clarity about shared responsibilities, account administration, logging, encryption, data location, backup and exit arrangements. Outsourcing operations does not remove the organization’s need to understand risks and requirements. Changes to an LMS integration or hosting provider can trigger reassessment.

Plan incident response before an incident occurs. Define reporting paths, triage, authority, preservation of evidence, containment, recovery, communication and learning. Use synthetic exercises; do not attack real systems. Notifications depend on applicable laws and contracts rather than a universal ISO deadline.

NIST SP 800-61 Rev. 3 was published in 2025 and aligns incident-response recommendations with CSF 2.0. It is a supplementary 2025 resource, not an amendment to ISO/IEC 27001. For Cedar Learning, a compromised instructor account calls for authorized containment, review of access and logs, an exposure assessment, communications decisions and tracked follow-up.''',
'''Tabletop only: an instructor reports an unexpected login and a suspected download of learner data.
1. Prepare an incident log with timestamps, facts, uncertainty and evidence owner.
2. Assign incident commander, IT investigator and communications decision-maker.
3. Propose authorized containment, evidence preservation and recovery steps.
4. List legal/contractual notification questions without inventing deadlines.
5. Review the cloud supplier responsibility matrix and identify logging gaps.
6. Record three lessons learned and assign corrective actions.
Deliverable: tabletop report, supplier matrix and action log. Acceptance: facts separated from assumptions, preserved evidence and approved communication paths.''',
['iso','controls','incident','csf'],[
q('What changed with NIST SP 800-61 Rev. 3 in 2025?',['Supporting incident-response guidance was updated; it is not a new ISO edition','ISO/IEC 27001 was renamed','Incident logs became unnecessary','All breaches gained the same reporting deadline'],'NIST guidance is supplementary and separate from ISO standards.'),
q('What does shared responsibility require?',['Explicitly identifying customer and provider security responsibilities','Assuming the provider handles every control','Ignoring supplier changes','Publishing administrator credentials'],'Responsibilities and evidence must be understood rather than assumed.'),
q('Which incident action is appropriate first?',['Follow authorized triage and preserve relevant evidence','Delete every log','Publicly speculate about victims','Test attacks against unrelated systems'],'Planned, authorized response supports reliable decisions and evidence handling.')]),
('Continuity, recovery and climate-related scenarios',75,
'''Information-security continuity and ICT readiness connect disruption planning to acceptable service outcomes. Identify critical activities and dependencies, determine recovery needs and test the arrangements. Business-impact analysis is a useful technique for understanding consequences over time; ISO/IEC 27001 does not prescribe one universal recovery target.

Recovery time objective (RTO) expresses the target time to restore a service. Recovery point objective (RPO) expresses the acceptable point to which data is recovered, often expressed as a time-based data-loss tolerance. Backups are one component: restoration capability, credentials, dependencies, communications and staff availability also matter.

Connect relevant climate issues from lesson 2 to practical scenarios. Heat-related outages or flooding at an infrastructure provider may require alternate connectivity, supplier assurance or changed recovery arrangements. The amendment asks for consideration of relevance; it does not mean every organization must purchase identical resilience technology.

For Cedar Learning, define separate recovery needs for live examinations and historic training records. Test with synthetic records in an isolated training folder. Record expected versus observed recovery, gaps and decisions. A backup job reporting success is not equivalent to a successful restore.''',
'''1. Define proposed RTO and RPO values for examinations, LMS content and learner records, with business rationale.
2. Map dependencies: hosting, identity service, internet, support staff and payment provider.
3. Back up a folder containing only synthetic text files; change a file and restore into a separate folder.
4. Compare hashes or contents to verify recovery; record elapsed time and data loss.
5. Tabletop a severe-weather outage and identify alternate operations and communications.
Deliverable: recovery objectives, dependency map and restore-test record. Acceptance: isolated non-production exercise, verified restored content, and documented gaps against objectives.''',
['iso','controls','climate','csf'],[
q('What does RPO describe?',['Acceptable recovery point/data-loss tolerance','The maximum employee count','The price of backups','Time to approve a policy'],'RPO concerns how far back restored information may be; RTO concerns restoration time.'),
q('What best validates a backup arrangement?',['A verified restore with results compared to recovery objectives','A successful job status alone','A vendor brochure','An untested written claim'],'Recovery evidence must demonstrate usable restoration.'),
q('How should relevant climate risks be handled?',['Carry justified effects into risk and continuity decisions','Apply the same technology purchase to everyone','Remove all supplier reviews','Ignore them after checking a box'],'Relevant context should inform proportionate management-system decisions.')]),
('Monitoring, internal audit and management review',75,
'''Clause 9 evaluates performance through monitoring, measurement, analysis, evaluation, internal audit and management review. Decide what needs monitoring, suitable methods, timing, responsibility and how results will be interpreted. Indicators should expose whether controls and objectives work, not only whether documents exist.

Internal audits evaluate conformity with the organization’s requirements and the standard’s requirements, and whether the ISMS is effectively implemented and maintained. Plan audits with relevant criteria and scope, consider process importance and previous results, and maintain auditor objectivity and impartiality. Sampling requires clear limitations; a small sample cannot justify claims about unexamined operations.

Collect evidence through records, observation and interviews. Separate observations from conclusions. If an access-review procedure requires quarterly completion but a completed review cannot be demonstrated for the period, describe the requirement, observed evidence and gap without inventing evidence.

Management review considers the system’s continuing suitability, adequacy and effectiveness and produces decisions about improvement and necessary changes. Prepare useful information on actions, changes, performance, audits, risks and improvement opportunities. Record decisions, owners and follow-up rather than simply a calendar invitation.''',
'''1. Define four metrics, including data source, owner, frequency, target and action threshold.
2. Create an internal-audit plan covering access management and incident response with scope, criteria and impartial auditor.
3. Inspect a synthetic evidence set containing one overdue access review and write a requirement/evidence/gap finding.
4. Draft a management-review agenda and decision log using the risk, incident and continuity results from earlier lessons.
Deliverable: metrics dashboard specification, audit plan/finding and review decision log. Acceptance: traceable evidence, explicit sampling limits and assigned decisions.''',
['iso','csf'],[
q('What supports an audit finding?',['A criterion, objective evidence and the identified gap','An unsupported opinion','A marketing slide','A guessed employee intention'],'Findings should be evidence-based and traceable to criteria.'),
q('What helps preserve audit impartiality?',['Avoiding review of one’s own work or arranging independent review','Having each operator certify only their own work','Ignoring conflicts','Removing all audit criteria'],'Objectivity and impartiality require appropriate audit assignments.'),
q('What should management review produce?',['Decisions and actions about improvement and needed changes','Only a meeting invitation','Automatic certification','A list of passwords'],'Review outputs should drive accountable follow-up.')]),
('Corrective action and the 2025 transition capstone',90,
'''Clause 10 addresses continual improvement and nonconformity/corrective action. A correction fixes the immediate problem; corrective action addresses causes so recurrence is less likely. Respond to the issue, evaluate causes and similar possible problems, implement action, and review effectiveness. Avoid closing a finding merely because a document was edited.

For an overdue access review, correcting the issue means completing the review and addressing inappropriate access. Causes could include unclear ownership or an ineffective reminder/escalation process. Corrective action might assign ownership and add escalation, followed by evidence from subsequent cycles that the process works.

The 2013-to-2022 certification transition had a 31 October 2025 completion deadline under IAF MD 26. Since that date is in the past, a legacy 2013 certificate must not be represented as current accredited ISO/IEC 27001:2022 certification. Check the certificate scope, edition, dates, issuing body and accreditation status with appropriate authoritative records. This course does not validate anyone’s certificate.

A transition assessment examines changes in management requirements and the revised controls, updates risk treatment and the SoA, identifies evidence gaps, and coordinates applicable certification activities with the certification body. The 2024 climate amendment must also be considered. A checklist is a planning aid, not proof of conformity.

Capstone: assemble a coherent small ISMS evidence pack from your labs. Trace one important risk from context through assessment, treatment, evidence, monitoring and improvement. Peer review the pack and record what still needs licensed-standard review or specialist advice.''',
'''1. Investigate the overdue access-review finding: document correction, cause analysis, corrective action, owner and effectiveness check.
2. Build a gap checklist for ISO/IEC 27001:2022 and Amendment 1:2024; include the revised SoA and climate relevance record.
3. Review a fictional certificate marked ISO/IEC 27001:2013 and record why a 2025 transition deadline is not evidence of successful transition.
4. Assemble scope, policy, risk register, SoA, treatment plan, evidence, audit and review records.
5. Trace one risk end-to-end and perform a peer review.
Deliverable: corrective-action record, transition gap plan and capstone evidence index. Acceptance: effectiveness verification, honest gaps, and no unsupported certification claim.''',
['iso','transition','climate','controls'],[
q('How does corrective action differ from correction?',['It addresses causes to prevent recurrence, rather than only fixing the immediate issue','It means deleting the finding','It only changes the course title','It always means buying software'],'Corrective action includes cause evaluation and effectiveness review.'),
q('What does a transition checklist prove on its own?',['It is a planning aid, not proof of certification or conformity','Guaranteed certification','That all controls work','That a 2013 certificate remains current indefinitely'],'Evidence and appropriate certification assessment are still required.'),
q('When should a corrective action be closed?',['After appropriate implementation and effectiveness evidence are reviewed','When a reminder email is sent','When the issue is renamed','Before causes are considered'],'Closure should be supported by evidence that action was effective.')]),
]

def build():
    lessons=[]
    for i,(title,minutes,content,lab,refs,quiz) in enumerate(DATA,1):
        attribution='\n\nSources and reading\n'+'\n'.join(f'- {SOURCES[k][0]}: {SOURCES[k][1]}' for k in refs)
        workbook=f'CyberAcademy | Lesson {i}: {title}\n\nOriginal practice worksheet\n\n{lab}\n\nEvidence table\nItem | Owner | Decision/rationale | Evidence | Review date\n\nSelf-review\nWhat worked?\nWhat is missing?\nWhat will change?\n'+attribution
        raw=workbook.encode()
        refs=list(dict.fromkeys(refs+['community']))
        attribution+='\n- '+SOURCES['community'][0]+': '+SOURCES['community'][1]
        resources=[{'type':'link','title':SOURCES[k][0],'url':SOURCES[k][1]} for k in refs]
        resources.append({'type':'worksheet','title':f'Lesson {i} lab workbook (original)','fileName':f'iso27001-lesson-{i:02d}-workbook.txt','fileSize':len(raw),'file':{'data':base64.b64encode(raw).decode(),'mimeType':'text/plain'}})
        lessons.append({'title':title,'slug':slugify(title),'description':content.split('\n\n')[0],'content':f'Lesson {i} · {title}\n\nLearning goals: explain the topic, apply it to Cedar Learning, and retain useful evidence.\n\n'+content+attribution+'\n\nSource status: ISO27001security.com is supplementary community guidance, not the normative standard. Official reading links are supplied, but live retrieval was blocked by the environment network policy during authoring. Exact requirements should be checked against licensed ISO documents. Supporting NIST guidance is not an ISO requirement.','headerImage':'','videoUrl':'','durationMinutes':minutes,'sortOrder':i,'isPublished':True,'lab':{'imageUrl':'','instructions':lab},'quiz':quiz,'resources':resources})
    return {'course':{'title':'Introduction to ISO 27001 ISM','slug':'introduction-to-iso-27001-ism','subtitle':'ISO/IEC 27001:2022 + Amendment 1:2024, with the 2025 transition and incident-response guidance','description':'An introductory, evidence-focused ISMS course with ten lessons, original practical labs, thirty quiz questions, official web reading links and downloadable worksheets. Baseline: ISO/IEC 27001:2022 with Amendment 1:2024. The 2025 topic is the accredited certification transition ending 31 October 2025, not an ISO/IEC 27001:2025 edition. NIST SP 800-61 Rev. 3 (2025) is supplementary guidance. Source links await live verification because the authoring environment blocked their domains. This learning course does not grant professional or ISO certification and does not replace the licensed standards.','level':'beginner','language':'en','currency':'USD','price':0,'originalPrice':0,'durationHours':sum(l['durationMinutes'] for l in lessons)/60,'thumbnailUrl':'','isPublished':True,'isFeatured':True,'isFree':True,'certificationIncluded':False,'category':{'name':'Governance, Risk & Compliance','slug':'governance-risk-compliance'},'tags':['ISO 27001','ISMS','2022 edition','2024 climate amendment','2025 transition','GRC'],'requirements':['No prior ISO knowledge required','Basic familiarity with business information and cloud services','Use only synthetic data for labs','Access to licensed ISO documents for exact implementation requirements'],'objectives':['Explain the ISMS and distinguish standards editions from transition dates','Define context and scope, including climate-change relevance','Create a policy, risk register, treatment plan and sample SoA','Practice operational controls, incident response and recovery','Plan internal audit, management review and corrective action']},'lessons':lessons}
if __name__=='__main__':
    pkg=build();(ROOT/'seeds/iso27001-introduction.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2))
    (ROOT/'seeds/iso27001-introduction.course.xml').write_bytes(serialize_package(pkg))
    print(f'Generated {len(pkg["lessons"])} lessons; {sum(len(l["quiz"]) for l in pkg["lessons"])} questions; {pkg["course"]["durationHours"]} hours')
