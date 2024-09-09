import pandas
import json
from langchain import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.prompts.chat import HumanMessagePromptTemplate
from pydantic import BaseModel, Field, validator
from typing import Optional
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate


class JobDescritionStore:
    j = []
    def init(self):
        self.j = []

    def load_csv(self, data_name='data.csv'):
    #loads the csc file and adds the discriptions into a list
        df = pandas.read_csv(data_name)
        for index, row in df.iterrows():
            desc = row['Job Description']
            new_desc = Job_descritor(desc)
            self.j.append(new_desc)
        return(self.j) 

    def save_json(self, file_name='data.json'):
    #saves json file
        desc_list = []
        for item in desc_list:
            desc_list.append(item.__dict__)
        with open(file_name, "w") as fp:
            json.dump(desc_list, fp, indent=4)   
        return 
    
class Job_descritor:
#defines the lists of the soft, tech, and technologies skills
    def __init__(self, desc):
        self.desc = desc
        self.soft_skills = []
        self.tech_skills = []
        self.technologies = []
   
    def get_desc(self):
        return self.desc
   
    def get_soft_skills(self):
        return self.soft_skills
   
    def get_tech_skills(self):
        return self.tech_skills

    def get_technologies(self):
        return self.technologies

    def set_soft_skills(self, soft_skills):
        self.soft_skills = soft_skills

    def set_tech_skills(self, tech_skills):
        self.tech_skills = tech_skills

    def set_technologies(self, technologies):
        self.technologies = technologies
 

class Job_descriptor_output(BaseModel):
#formats the lists
    tech_skills: Optional[list] = None
    soft_skills: Optional[list] = None
    technologies: Optional[list] = None

class JobProcessor:
    def __init__(self, open_api_key, temperature, model, template):
    #opens the llm and opens the human message prompt
        self.open_api_key = open_api_key
        self.temperature = temperature
        self.model = model
        self.llm = OpenAI(openai_api_key = openai_api_key, temperature = temperature)
        self.template = template
        self.hm = None #HumanMessagePromptTemplate.from_template(template)

    def get_llm(self):
        return self.llm
    
    def get_hm(self):
        return self.hm
    
    def set_template(self):
        return self.template
    
    def job_finder_1(self, job_description):
        output_parser = CommaSeparatedListOutputParser()
        format_instructions = output_parser.get_format_instructions()
        prompt = PromptTemplate(
            template= self.template,
            input_variables= ["job_description"],
            partial_variables= {"format_instructions": format_instructions}
        )
        input = prompt.format(job_description=job_description)
        output = self.get_llm()(input)
        final = output_parser.parse(output)
        return final


if __name__ == "__main__":
    with open('env.json') as json_file:
        data = json.load(json_file)
        openai_api_key = data['openai_api_key']
        temperature = data['openai_temperature']
        model = data['openai_model']
    template_tech = """/
    Please extract technical skills from the following job description and store it in tech_skills.
    \n{job_description}\n{format_instructions}
    """
    template_soft = """/
    Please extract soft skills from the following job description and store it in soft_skills.
    \n{job_description}\n{format_instructions}
    """
    template_technologies = """/
    Please extract technologies from the following job description and store it in technologies.
    \n{job_description}\n{format_instructions}
    """
    job_desc_store = JobDescritionStore()
    job_desc_store.load_csv()
    procs_tech = JobProcessor(openai_api_key, temperature, model, template_tech)
    procs_soft = JobProcessor(openai_api_key, temperature, model, template_soft)
    procs_technologies = JobProcessor(openai_api_key, temperature, model, template_technologies)
    main_list = []
    for desc in job_desc_store.j[:20]:
        print(desc.desc)
        final_tech = procs_tech.job_finder_1(desc.desc)
        final_soft = procs_soft.job_finder_1(desc.desc)
        final_technologies = procs_technologies.job_finder_1(desc.desc)
        main_dict = {'tech_skills': final_tech, 'soft_skills': final_soft, 'technologies': final_technologies}
        main_list.append(main_dict)
    print(main_list)
    with open("analyzed_skills.json", "w") as fp:
        json.dump(main_list, fp, indent=4)
    job_desc_store.save_json()