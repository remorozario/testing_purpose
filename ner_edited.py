import re
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import nltk
import spacy
from spacy.matcher import Matcher

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

class ResumeParser:
    name_pattern = re.compile(r'\b[A-Z][a-zA-Z]+\b')
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)

    # Method takes a path to a PDF file as input and converts it into plain text

    def convert_pdf_to_txt(self, path):
        if path.endswith(".pdf"):
            rsrcmgr = PDFResourceManager()
            retstr = StringIO()
            laparams = LAParams()
            device = TextConverter(rsrcmgr, retstr, laparams=laparams)
            fp = open(path, 'rb')
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            password = ""
            maxpages = 0
            caching = True
            pagenos = set()

            for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
                interpreter.process_page(page)

            text = retstr.getvalue()

            fp.close()
            device.close()
            retstr.close()
            return text
        else:
            raise ValueError("Not supported format: Only PDF files are allowed.")
    
    def getPhone(self, text):
        try:
            pattern = re.compile(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
            phone = pattern.findall(text)
            phone = [re.sub(r'[,.]', '', el) for el in phone if len(re.sub(r'[()\-.,\s+]', '', el))>6]
            phone = [re.sub(r'\D$', '', el).strip() for el in phone]
            phone = [el for el in phone if len(re.sub(r'\D','',el)) <= 13 and len(re.sub(r'\D','',el))>=10]
            return phone[0] if phone else None
        except:
            return None

    def getEmail(self, text):
        try:
            pattern = re.compile(r'\S*@\S*')
            email = pattern.findall(text)
            return email[0] if email else None
        except:
            return None

    def getExperience(self, sentences):
        try:
            experience_keywords = ['experience', 'internship', 'work', 'position', 'job', 'project', 'role', 'responsibility', 'task', 'duty', 'employment', 'professional', 'career', 'industry', 'organization', 'company', 'team', 'leadership', 'management', 'accomplishment', 'achievement', 'success', 'contribution', 'client', 'deadline', 'technology', 'tool', 'software', 'system', 'database', 'framework', 'methodology', 'problem-solving', 'collaboration', 'communication', 'initiative', 'innovation', 'multitasking', 'adaptability', 'teamwork', 'remote', 'remote work', 'virtual', 'virtual team', 'global', 'international', 'cross-functional', 'agile', 'scrum', 'project management', 'time management', 'organizational', 'analytical', 'research', 'presentation', 'negotiation', 'client interaction', 'customer service', 'training', 'mentoring', 'coaching', 'performance evaluation', 'feedback', 'process improvement', 'quality assurance', 'sales', 'marketing', 'financial', 'budgeting', 'revenue', 'cost', 'growth', 'strategy', 'planning', 'execution', 'analysis', 'reporting', 'regulatory', 'compliance', 'legal', 'contract', 'risk management', 'healthcare', 'patient care', 'clinical', 'education', 'teaching', 'curriculum development', 'teamwork', 'problem-solving', 'critical thinking', 'adaptability']
            
            sen=[]
            z=0
            for words in sentences:
                for i in range(len(words)):
                    if words[i][0].lower() in experience_keywords:
                        index = [z, i]
                        break
                z += 1

            exp = []
            current_exp = []
            for i in sentences[index[0]][index[1]+1:]:
                if i[0].isalpha() and i[1] == 'NNP':
                    current_exp.append(i[0])
                elif current_exp:
                    exp.append(' '.join(current_exp))
                    current_exp = []
            if current_exp:
                exp.append(' '.join(current_exp))

            return exp
            
        except:
            return None

    def getQual(self, sentences):
        quals_it = ['Data Science', 'Computer Science', 'Information Technology', 'Software Engineering', 'Web Development', 'Database Management', 'Networking']
        quals_sales_marketing = ['Marketing', 'Business Administration', 'Market Research', 'Digital Marketing', 'Advertising', 'Public Relations']
        quals_finance_accounting = ['Finance', 'Accounting', 'Economics', 'Financial Analysis', 'Budgeting', 'Financial Reporting', 'Auditing', 'Risk Management']
        quals_hr = ['Human Resources', 'Business Administration', 'Organizational Psychology', 'Employee Relations', 'Training and Development', 'Recruitment', 'Compensation and Benefits']
        quals_operations_supplychain = ['Operations Management', 'Supply Chain Management', 'Logistics', 'Inventory Management', 'Quality Control', 'Process Improvement']
        quals_customer_service = ['Customer Service', 'Communication Skills', 'Problem-solving']
        quals_healthcare = ['Nursing', 'Medicine', 'Healthcare Administration', 'Medical Coding', 'Patient Care', 'Clinical Research']
        quals_education = ['Teaching', 'Curriculum Development', 'Instructional Design', 'Student Assessment', 'Educational Technology']
        quals_legal = ['Law', 'Legal Studies', 'Contract Law', 'Litigation', 'Legal Research']

        quals = {
            'IT Department': quals_it,
            'Sales and Marketing Department': quals_sales_marketing,
            'Finance and Accounting Department': quals_finance_accounting,
            'Human Resources Department': quals_hr,
            'Operations and Supply Chain Department': quals_operations_supplychain,
            'Customer Service Department': quals_customer_service,
            'Healthcare Department': quals_healthcare,
            'Education Department': quals_education,
            'Legal Department': quals_legal
        }

        qual = []
        for words in sentences:
            for department, keywords in quals.items():
                for i in range(len(words)):
                    if words[i][0] in keywords:
                        qual.append((" ".join([words[k][0] for k in range(i + 1, len(words))])))
                        break

        return qual if qual else None

    def getSkills(self, sentences):
        it_skills = ['Python', 'Java', 'C++', 'HTML', 'CSS', 'JavaScript', 'SQL', 'Agile', 'DevOps', 'Data Science', 'Machine Learning', 'Artificial Intelligence', 'Cloud Computing', 'Big Data', 'Web Development', 'Mobile App Development', 'Software Testing', 'Networking']

        sales_marketing_skills = ['Sales', 'Marketing', 'Business Development', 'Lead Generation', 'Market Research', 'Digital Marketing', 'Advertising', 'Customer Relationship Management (CRM)', 'Branding']

        finance_accounting_skills = ['Finance', 'Accounting', 'Financial Analysis', 'Budgeting', 'Financial Reporting', 'Auditing', 'Risk Management', 'Investment Analysis', 'Bookkeeping']

        hr_skills = ['Human Resources', 'Recruitment', 'Talent Acquisition', 'Employee Relations', 'Performance Management', 'Training and Development', 'Compensation and Benefits']

        operations_supplychain_skills = ['Operations Management', 'Supply Chain Management', 'Logistics', 'Inventory Management', 'Quality Control', 'Process Improvement', 'Project Management']

        customer_service_skills = ['Customer Service', 'Customer Support', 'Client Management', 'Complaint Resolution', 'Communication Skills']

        healthcare_skills = ['Healthcare', 'Nursing', 'Medical Coding', 'Medical Billing', 'Patient Care', 'Clinical Research', 'Healthcare IT']

        education_skills = ['Teaching', 'Curriculum Development', 'Instructional Design', 'Classroom Management', 'Student Assessment', 'Educational Technology']

        legal_skills = ['Legal', 'Contract Drafting', 'Legal Research', 'Litigation', 'Corporate Law', 'Contract Negotiation']

        # Combine all department-specific skills
        all_skills = it_skills + sales_marketing_skills + finance_accounting_skills + hr_skills + operations_supplychain_skills + customer_service_skills + healthcare_skills + education_skills + legal_skills

        # Extract skills from the text
        skills = []
        for sentence in sentences:
            for word, pos in sentence:
                if word in all_skills:
                    skills.append(word)

        return list(set(skills)) if skills else None

    def getCertification(self, sentences):
        it_certifications = [
            'Microsoft Certified: Azure Administrator Associate',
            'Microsoft Certified: Azure Developer Associate',
            'Microsoft Certified: Azure Solutions Architect Expert',
            'Cisco Certified Network Associate (CCNA)',
            'Cisco Certified Network Professional (CCNP)',
            'CompTIA A+ Certification',
            'CompTIA Network+ Certification',
            'CompTIA Security+ Certification',
            'AWS Certified Solutions Architect - Associate',
            'AWS Certified Developer - Associate',
            'AWS Certified SysOps Administrator - Associate',
            'Google Certified Professional Cloud Architect',
            'Google Certified Professional Data Engineer',
            'Oracle Certified Associate (OCA)',
            'Oracle Certified Professional (OCP)',
            'Certified Ethical Hacker (CEH)',
            'Certified Information Systems Security Professional (CISSP)',
            'Certified Information Security Manager (CISM)',
            'Project Management Professional (PMP)',
            'Certified ScrumMaster (CSM)',
            'ITIL Foundation Certification',
            'VMware Certified Professional (VCP)',
            'Salesforce Certified Administrator',
            'Salesforce Certified App Builder',
            'Salesforce Certified Platform Developer',
            'Certified Data Professional (CDP)',
            'Certified Analytics Professional (CAP)',
            'Certified in Risk and Information Systems Control (CRISC)',
            'Certified Information Privacy Professional (CIPP)',
        ]

        sales_marketing_certifications = [
            'Certified Professional Salesperson (CPS)',
            'Certified Sales Executive (CSE)',
            'Certified Marketing Professional (CMP)',
            'Digital Marketing Certified Associate (DMCA)',
            'Social Media Marketing Certification',
            'Google Ads Certification',
            'HubSpot Inbound Marketing Certification',
            'Salesforce Certified Sales Cloud Consultant',
            'Hootsuite Social Marketing Certification',
            'Content Marketing Certification (Content Marketing Institute)',
        ]

        finance_accounting_certifications = [
            'Certified Public Accountant (CPA)',
            'Chartered Financial Analyst (CFA)',
            'Certified Management Accountant (CMA)',
            'Certified Financial Planner (CFP)',
            'Certified Internal Auditor (CIA)',
            'Certified Fraud Examiner (CFE)',
            'Certified Government Financial Manager (CGFM)',
            'Certified Payroll Professional (CPP)',
            'Certified Treasury Professional (CTP)',
            'Certified Bookkeeper (CB)',
        ]

        hr_certifications = [
            'Professional in Human Resources (PHR)',
            'Senior Professional in Human Resources (SPHR)',
            'SHRM Certified Professional (SHRM-CP)',
            'SHRM Senior Certified Professional (SHRM-SCP)',
            'Certified Compensation Professional (CCP)',
            'Certified Benefits Professional (CBP)',
            'Certified Training and Development Professional (CTDP)',
            'Certified Employee Benefits Specialist (CEBS)',
            'Certified Professional in Learning and Performance (CPLP)',
            'Global Professional in Human Resources (GPHR)',
        ]

        operations_supplychain_certifications = [
            'Certified Supply Chain Professional (CSCP)',
            'Certified in Production and Inventory Management (CPIM)',
            'Certified Professional in Healthcare Supply Chain Management (CHL)',
            'Certified Professional in Supplier Diversity (CPSD)',
            'Certified Professional in Logistics and Transportation (CPLT)',
            'Certified Professional in Demand Forecasting (CPDF)',
            'Certified Professional in Lean Six Sigma (CPLSS)',
            'Certified Professional in Warehouse Management (CPWM)',
            'Certified Professional in Manufacturing (CPM)',
            'Certified Professional in Distribution and Warehousing (CPDW)',
        ]

        customer_service_certifications = [
            'Certified Customer Service Professional (CCSP)',
            'Certified Professional in Customer Service (CPCS)',
            'Certified Call Center Manager (CCCM)',
            'Certified Customer Experience Professional (CXP)',
            'Certified Customer Success Manager (CSM)',
            'Certified Professional in Contact Center Management (CPCCM)',
            'Certified Customer Service Supervisor (CCSS)',
            'Certified Professional in Outsourcing Management (CPOM)',
            'Certified Professional in Customer Loyalty (CPCL)',
            'Certified Customer Service Auditor (CCSA)',
        ]

        healthcare_certifications = [
            'Registered Nurse (RN)',
            'Certified Nursing Assistant (CNA)',
            'Licensed Practical Nurse (LPN)',
            'Certified Medical Assistant (CMA)',
            'Certified Pharmacy Technician (CPhT)',
            'Certified Professional Coder (CPC)',
            'Certified Medical Billing Specialist (CMBS)',
            'Certified Clinical Research Professional (CCRP)',
            'Certified Healthcare Information Systems Security Practitioner (CHISSP)',
            'Certified Professional in Healthcare Information and Management Systems (CPHIMS)',
        ]

        education_certifications = [
            'Certified Teacher',
            'Certified Education Administrator',
            'Certified Education Counselor',
            'Certified Instructional Designer',
            'Certified Online Course Developer',
            'Certified Educational Technology Specialist',
            'Certified School Psychologist',
            'Certified Special Education Teacher',
            'Certified Education Consultant',
            'Certified School Principal',
        ]

        legal_certifications = [
            'Juris Doctor (JD)',
            'Certified Paralegal (CP)',
            'Certified Legal Assistant (CLA)',
            'Certified Legal Secretary (CLS)',
            'Certified Legal Manager (CLM)',
            'Certified Corporate Law Specialist (CCLS)',
            'Certified Intellectual Property Law Specialist (CIPLS)',
            'Certified Legal Administrator (CLA)',
            'Certified Legal Investigator (CLI)',
            'Certified Compliance and Ethics Professional (CCEP)',
        ]

        # Combine all department-specific certifications
        all_certifications = (
            it_certifications
            + sales_marketing_certifications
            + finance_accounting_certifications
            + hr_certifications
            + operations_supplychain_certifications
            + customer_service_certifications
            + healthcare_certifications
            + education_certifications
            + legal_certifications
        )

        try:
            sen = []
            z = 0
            global index
            for words in sentences:
                for i in range(len(words)):
                    if words[i][0].lower() == 'certifications':
                        index = [z, i]
                        break
                z += 1

            certis = " ".join([sentences[index[0]][k][0] for k in range(1, len(sentences[index[0]]))])

            matched_certifications = [cert for cert in all_certifications if cert.lower() in certis.lower()]

            return matched_certifications if matched_certifications else None
        except:
            return None


    def extract_name(self, text):
        # Tokenize the text into sentences
        sentences = nltk.sent_tokenize(text)

        # Extract proper nouns from each sentence
        proper_nouns = []
        for sentence in sentences:
            tokens = nltk.word_tokenize(sentence)
            tagged_tokens = nltk.pos_tag(tokens)
            for i in range(1, len(tagged_tokens)):
                if tagged_tokens[i-1][1] == 'NNP' and tagged_tokens[i][1] == 'NNP':
                    name = tagged_tokens[i-1][0] + ' ' + tagged_tokens[i][0]
                    proper_nouns.append(name)

        # Apply additional filters to select the most likely name
        filtered_names = []
        for name in proper_nouns:
            # Exclude names with less than 2 characters
            if len(name) < 2:
                continue
            filtered_names.append(name)

        return filtered_names[0] if filtered_names else None

    def getDetails(self, text):
        sentences = nltk.sent_tokenize(text)
        sentences = [nltk.word_tokenize(el) for el in sentences]
        sentences = [nltk.pos_tag(el) for el in sentences]
        phone = self.getPhone(text)
        mail = self.getEmail(text)
        exp = self.getExperience(sentences)
        quals = self.getQual(sentences)
        skills = self.getSkills(sentences)
        certis = self.getCertification(sentences)
        name = self.extract_name(text)
        details = {
            'Name': name,
            'Phone_no': phone,
            'Email': mail,
            'Experience': exp,
            'Qualification': quals,
            'Skills': skills,
            'Certifications': certis
        }
        return details
parser = ResumeParser()
text = parser.convert_pdf_to_txt("C:/Users/HP/OneDrive/Desktop/Athira K.pdf")


print("Extracted Text:")
print(text)
details = parser.getDetails(text)

categorized_data = {
    "Name": details["Name"],
    "Contact Information": {
        "Phone_no": details["Phone_no"],
        "Email": details["Email"],
    },
    "Experience": details["Experience"],
    "Qualification": details["Qualification"],
    "Skills": details["Skills"],
    "Certifications": details["Certifications"],

}

################################################################

import json

# Your existing code for parsing and getting details here

# Saving the details to a JSON file

output_file_path = "output_details.json"
with open(output_file_path, "w") as output_file:
    json.dump(details, output_file, indent=4)

print(f"Details categorized and saved to {output_file_path}")