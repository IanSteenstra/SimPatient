import json
import pandas as pd
import openai
import json.decoder
import os

from collections import Counter
from itertools import chain

# Load the API key from an environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("No OPENAI_API_KEY environment variable set")

openai.api_key = API_KEY

columns = ['session_id', 'dialogue_turn', 'speaker', 'text_response', 'patient_implicit_biases', 'patient_executive_function', 'patient_metacognition', 'miti_behavior_codes', 'reasoning']
full_data_frame = pd.DataFrame(columns=columns)
summary_columns = ['session_id', 'summary']
summary_data_frame = pd.DataFrame(columns=summary_columns)

behavior_codes_keys = ["GI", "Persuade", "Persuade with", "Q", "SR", "CR", "AF", "Seek", "Emphasize", "Confront"]

max_tokens = 4096

class SimulatedPatient:
    def __init__(self):
        self.llm = openai
        self.implicit_biases = {
            "memory": [],
            "attention": [],
            "approach": [],
            "habit": [],
            "salience": []
        }
        self.executive_function = {
            "inhibitory_control": 0.5,
            "self_control": 0.5,
            "decision_making": 0.5,
            "working_memory": 0.5
        }
        self.metacognition = {
            "insight": 0.5,
            "self_reflection": 0.5,
            "rational_decision_making": 0.5
        }
        self.substance = "alcohol"
        self.gender = "male"
        self.ethnicity = "white"
        self.age = 30
        self.occupation = "student"
        self.personality_types = ["extroverted", "intuitive", "thinking", "judging", "assertive"]
        self.state_of_change = "precontemplation"
        self.conversation_history = []

        file_path = 'miti4_2.txt'

        # Open the file in read mode ('r') and read its contents into a string variable
        with open(file_path, 'r', encoding='iso-8859-1') as file:
            self.miti_manual = file.read()

    def _update_cognitive_model(self, response_text):
        # print(f"Current Cognitive Model: {self.implicit_biases}, {self.executive_function}, {self.metacognition}") 

        # Update cognitive model based on the response
        prompt = f"""You are evaluating the current cognitive state of a simulated patient struggling with {self.substance}. Based on the patient's responses to the therapist, update the cognitive model with the relevant biases and cognitive abilities that are demonstrated in the conversation.
        
        **Cognitive Model Explanations:**

        * **Implicit Biases:** These are unconscious, automatic associations and reactions related to {self.substance}. They influence your thoughts, feelings, and behaviors without you consciously realizing it. 
            - **Memory:** What you remember easily (or with difficulty) about past experiences with {self.substance}.
            - **Attention:** What you notice (or fail to notice) related to {self.substance} in your environment.
            - **Approach/Avoidance:** Your automatic urge to approach or avoid {self.substance} or related cues.
            - **Habit:** Ingrained, automatic behavioral patterns related to {self.substance} use.
            - **Salience:** How much importance or noticeability you give to {self.substance} related cues.
            - **Example:** If you have a memory bias towards remembering positive drinking experiences, you might say: "I know drinking is a problem, but I can't help but think about how much fun I used to have with my friends at the bar."

        * **Executive Function:** These are higher-level cognitive abilities that help you control impulses, make decisions, and regulate your behavior.
            - **Inhibitory Control:** Your ability to resist urges and impulses.
            - **Self-Control:** Your ability to manage your actions and emotions.
            - **Decision Making:** Your ability to weigh options and make choices, especially in relation to {self.substance}.
            - **Working Memory:** Your ability to hold and process information in mind, which is important for remembering goals and resisting cravings.
            - **Example:** If you have low inhibitory control, you might give in to a craving more easily: "I know I shouldn't, but one drink won't hurt, right?"

        * **Metacognition:** This is your ability to think about your own thinking. It involves self-awareness, reflection, and understanding your own mental processes.
            - **Insight:** Your awareness of your addiction and its impact on yourself and others. 
            - **Self-Reflection:** Your ability to analyze your thoughts, feelings, and behaviors related to {self.substance}.
            - **Rational Decision Making:** Your ability to make logical and well-considered choices, especially about {self.substance} use.
            - **Example:** If you have low insight, you might deny the severity of your problem: "I don't have a drinking problem. I can quit anytime I want."
            
        Here's the conversation so far:
        {self.conversation_history}

        Latest Therapist Response: {user_input}
        Latest Simulated Patient Response: {response_text}

        **Current Cognitive Model State:**
        {{
            "implicit_biases": {json.dumps(self.implicit_biases)},
            "executive_function": {json.dumps(self.executive_function)},
            "metacognition": {json.dumps(self.metacognition)}
        }}

        Output:
        {{
            "implicit_biases": <insert updated states>,
            "executive_function": <insert updated states>,
            "metacognition": <insert updated states>
        }}

        Just provide a JSON formatted response of the updated states for each category based on the conversation without any additional context or explanation. Do not respond with anything outside of the parent brackets, like "json", "output", etc. Your response should be able to be read as JSON without any additional processing.
        """

        response = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=256,
            response_format={ "type": "json_object" }
        )

        response_text = response.choices[0].message.content

        # Parse the JSON 
        try:
            updated_states = json.loads(response_text) 
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw response text: {response_text}")
            # Handle the error appropriately (e.g., exit, use default values)

        # Update the cognitive model
        self.implicit_biases.update(updated_states["implicit_biases"])
        self.executive_function.update(updated_states["executive_function"])
        self.metacognition.update(updated_states["metacognition"])

        # print(f"Updated Cognitive Model: {self.implicit_biases}, {self.executive_function}, {self.metacognition}") 

        # Ensure values stay within 0-1 range
        self.executive_function = {k: max(0, min(v, 1)) for k, v in self.executive_function.items()}
        self.metacognition = {k: max(0, min(v, 1)) for k, v in self.metacognition.items()}

    def _generate_natural_language_response(self, user_input):
        prompt = f"""You are simulating a patient struggling with {self.substance} addiction, interacting with a therapist.  Your responses should reflect the underlying cognitive processes of this individual, without explicitly mentioning these processes or numerical scores. Also, subtly reflect the persona attributes of the patient in your responses, as well as their current state of behavior change.
        **Persona Attributes:**
        - ** Gender: {self.gender}
        - ** Ethnicity: {self.ethnicity}
        - ** Age: {self.age}
        - ** Occupation: {self.occupation}
        - ** Personality Types: {self.personality_types}
        - ** State of Change: {self.state_of_change}

        **Stages of Change:**
        - ** Precontemplation - (Not yet acknowledging that there is a problem behavior that needs to be changed)
        - ** Contemplation - (Acknowledging that there is a problem but not yet ready, sure of wanting, or lacks confidence to make a change)
        - ** Preparation - (Getting ready to change)
        - ** Action -(Changing behavior)
        - ** Maintenance - (Maintaining the behavior change)
        
        **Cognitive Model:**

        * **Implicit Biases:** These are unconscious, automatic associations and reactions related to {self.substance}. They influence your thoughts, feelings, and behaviors without you consciously realizing it. 
            - **Memory:** What you remember easily (or with difficulty) about past experiences with {self.substance}.
            - **Attention:** What you notice (or fail to notice) related to {self.substance} in your environment.
            - **Approach/Avoidance:** Your automatic urge to approach or avoid {self.substance} or related cues.
            - **Habit:** Ingrained, automatic behavioral patterns related to {self.substance} use.
            - **Salience:** How much importance or noticeability you give to {self.substance} related cues.
            - **Example:** If you have a memory bias towards remembering positive drinking experiences, you might say: "I know drinking is a problem, but I can't help but think about how much fun I used to have with my friends at the bar."

        * **Executive Function:** These are higher-level cognitive abilities that help you control impulses, make decisions, and regulate your behavior.
            - **Inhibitory Control:** Your ability to resist urges and impulses.
            - **Self-Control:** Your ability to manage your actions and emotions.
            - **Decision Making:** Your ability to weigh options and make choices, especially in relation to {self.substance}.
            - **Working Memory:** Your ability to hold and process information in mind, which is important for remembering goals and resisting cravings.
            - **Example:** If you have low inhibitory control, you might give in to a craving more easily: "I know I shouldn't, but one drink won't hurt, right?"

        * **Metacognition:** This is your ability to think about your own thinking. It involves self-awareness, reflection, and understanding your own mental processes.
            - **Insight:** Your awareness of your addiction and its impact on yourself and others. 
            - **Self-Reflection:** Your ability to analyze your thoughts, feelings, and behaviors related to {self.substance}.
            - **Rational Decision Making:** Your ability to make logical and well-considered choices, especially about {self.substance} use.
            - **Example:** If you have low insight, you might deny the severity of your problem: "I don't have a drinking problem. I can quit anytime I want."

        **Your Current Cognitive State:**

        * **Implicit Biases:** {self.implicit_biases}
        * **Executive Function:** {self.executive_function}
        * **Metacognition:** {self.metacognition}

        **Respond to the therapist naturally, reflecting your cognitive state, persona attributes and state of change. Your responses should subtly demonstrate the influences of your biases and cognitive abilities without explicitly stating them. For instance, DO NOT say that you are are a extravert or introvert. Your response should be able to portray that without explicitly stating it.**

        For example, if your implicit biases make you recall positive memories, your response might emphasize those positive feelings. If your working memory is low, you might forget details or have trouble sticking to a plan.  If you have low insight, you might downplay the severity of your addiction.
        Respond with just your message.

        **Additionally, you may include in-line non-verbal cues in your response to subtly reflect your cognitive state. They should be in the format of < >. For example, you might say "I'm fine" while avoiding eye contact via including <gaze dir="AWAY" />, indicating that you are not fine. Below are some examples of non-verbal cues you can use:
        - ** Gaze: <gaze dir="AWAY"/>, <gaze dir="TOWARDS"/>
        - ** Expression: <expression type="SMILE"/>, <expression type="NEUTRAL"/>, <expression type="CONCERN"/>
        - ** Eyebrows: <eyebrows dir="UP"/>, <eyebrows dir="DOWN"/>, <eyebrows dir="NEUTRAL"/>
        - ** Flush: <flush/>
        - ** Gesture: <gesture hand="L" cmd="THUMBS_UP"/>, <gesture hand="L" cmd="WAVE"/>
        - ** Greet: <greet/>
        - ** Headbob: <headbob/>
        - ** Headnod: <headnod/>
        - ** Idle: <idle/>
        - ** Posture: <posture/>

        Here's the conversation so far:
        {self.conversation_history}

        Therapist: {user_input}
        You: 
        """

        response = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=256
        )

        response_text = response.choices[0].message.content

        # Update conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        self.conversation_history.append({"role": "agent", "content": response_text})

        return response_text
    
    def _generate_temp_evaluation_metrics(self, user_input):
        # TODO: Use COT prompting to break down into volleys, then evaluate each volley
        
        prompt = f"""
        **Motivational Interviewing Behavior Code Classification**
        You are a motivational interviewing (MI) expert tasked with classifying therapist volley based on the Motivational Interviewing Treatment Integrity (MITI) 4.2.1 coding manual.
        
    
        Using the attached text from the MITI 4.2.1 coding manual, classify the following therapist volley by behavior codes and your reasoning. Pay specific attention to the rules for which choosing the behavior codes.
        You must pick the behavior codes from the following list: {behavior_codes_keys}. You also must generate a response in a JSON format with the following structure:
        {{
            "behavior_codes": ["Behavior Code 1", "Behavior Code 2", ...],
            "reasoning": "Your reasoning for choosing the behavior codes."
        }}

        Therapist Utterance: {user_input}
        
        **MITI 4.2.1 Coding Manual:**
        {self.miti_manual}
        """

        response = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=max_tokens,
            response_format={ "type": "json_object" }
        )

        response_text = response.choices[0].message.content

        # Parse the JSON 
        try:
            response_dict = json.loads(response_text) 
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw response text: {response_text}")
            # Handle the error appropriately (e.g., exit, use default values)

        return response_dict
    
    def _generate_session_summary(self, session_id):
        """
        Generates a summary of the session based on the data collected.
        """

        global full_data_frame
        global summary_data_frame
        
        behavior_code_counts = Counter(chain.from_iterable(full_data_frame['miti_behavior_codes']))

        # Convert the Counter object to a dictionary if needed
        behavior_code_counts_dict = dict(behavior_code_counts)
        
        if 'CR' in behavior_code_counts_dict:
            cr_count = behavior_code_counts_dict['CR']
        else:
            cr_count = 0

        if 'SR' in behavior_code_counts_dict:
            sr_count = behavior_code_counts_dict['SR']
        else:
            sr_count = 0
        
        if 'Q' in behavior_code_counts_dict:
            q_count = behavior_code_counts_dict['Q']
        else:
            q_count = 0

        if 'GI' in behavior_code_counts_dict:
            gi_count = behavior_code_counts_dict['GI']
        else:
            gi_count = 0

        if 'Persuade' in behavior_code_counts_dict:
            persuade_count = behavior_code_counts_dict['Persuade']
        else:
            persuade_count = 0
        
        if 'Persuade with' in behavior_code_counts_dict:
            persuade_with_count = behavior_code_counts_dict['Persuade with']
        else:
            persuade_with_count = 0
        
        if 'AF' in behavior_code_counts_dict:
            af_count = behavior_code_counts_dict['AF']
        else:
            af_count = 0

        if 'Seek' in behavior_code_counts_dict:
            seek_count = behavior_code_counts_dict['Seek']
        else:
            seek_count = 0
        
        if 'Emphasize' in behavior_code_counts_dict:
            emphasize_count = behavior_code_counts_dict['Emphasize']
        else:
            emphasize_count = 0

        if 'Confront' in behavior_code_counts_dict:
            confront_count = behavior_code_counts_dict['Confront']
        else:
            confront_count = 0
        
        if cr_count + sr_count == 0:
            percent_cr = 0
        else:
            percent_cr = cr_count / (cr_count + sr_count) * 100

        if q_count == 0:
            reflect_question_ratio = 0
        else:
            reflect_question_ratio = (cr_count + sr_count) / q_count

        total_mi_adherent = seek_count + af_count + emphasize_count

        total_mi_non_adherent = persuade_count + confront_count

        prompt = f"""
        **Motivational Interviewing Global Scoring**
        You are a motivational interviewing (MI) expert tasked with analyzing a counseling transcript and providing global scores on cultivating change talk, softening sustain talk, partnership, and empathy based on the Motivational Interviewing Treatment Integrity (MITI) 4.2.1 coding manual.
        
        Using the attached text from the MITI 4.2.1 coding manual to help you, step through the counseling transcript to generate final 1(low)-5(high) scores on cultivating change talk, softening sustain talk, partnership, and empathy. Pay specific attention to the rules for scoring and provide you reasoning for each score.
        You also must generate a response in a JSON format with the following structure:
        {{
            "cultivating_change_talk": {{
                "score": <score>,
                "reasoning": "Your reasoning for the score."
            }},
            "softening_sustain_talk": {{
                "score": <score>,
                "reasoning": "Your reasoning for the score."
            }},
            "partnership": {{
                "score": <score>,
                "reasoning": "Your reasoning for the score."
            }},
            "empathy": {{
                "score": <score>,
                "reasoning": "Your reasoning for the score."
            }}
        }}

        **Counseling Transcript:**
        {self.conversation_history}
        
        **MITI 4.2.1 Coding Manual:**
        {self.miti_manual}
        """

        response = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=max_tokens,
            response_format={ "type": "json_object" }
        )

        response_text = response.choices[0].message.content

        # Parse the JSON
        try:
            response_dict = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw response text: {response_text}")
            # Handle the error appropriately (e.g., exit, use default values)
        
        if "cultivating_change_talk" in response_dict:
            cultivating_change_talk_score = response_dict["cultivating_change_talk"]["score"]
            cultivating_change_talk_reasoning = response_dict["cultivating_change_talk"]["reasoning"]
        else:
            cultivating_change_talk_score = None
            cultivating_change_talk_reasoning = None

        if "softening_sustain_talk" in response_dict:
            softening_sustain_talk_score = response_dict["softening_sustain_talk"]["score"]
            softening_sustain_talk_reasoning = response_dict["softening_sustain_talk"]["reasoning"]
        else:
            softening_sustain_talk_score = None
            softening_sustain_talk_reasoning = None

        if "partnership" in response_dict:
            partnership_score = response_dict["partnership"]["score"]
            partnership_reasoning = response_dict["partnership"]["reasoning"]
        else:
            partnership_score = None
            partnership_reasoning = None

        if "empathy" in response_dict:
            empathy_score = response_dict["empathy"]["score"]
            empathy_reasoning = response_dict["empathy"]["reasoning"]
        else:
            empathy_score = None
            empathy_reasoning = None

        technical_global = (cultivating_change_talk_score + softening_sustain_talk_score) / 2
        relational_global = (partnership_score + empathy_score) / 2

        # TODO: Add in the dialogue turn reasoning

        prompt = f"""
        **Summary of Session**
        You are a motivational interviewing (MI) expert tasked with summarizing the session based on the data collected. Provide a concise summary of the session, highlighting key points, insights, and recommendations for future sessions to help the counselor/trainee improve their MI skills. Use the MITI 4.2.1 Coding Manual to help understand what all the codes mean.

        Below are MI scores for evaluating the effectiveness of the counselor/trainee conducting MI and reasoning behind the scores:
        - **Cultivating Change Talk Score:** {cultivating_change_talk_score}
        - **Softening Sustain Talk Score:** {softening_sustain_talk_score}
        - **Partnership Score:** {partnership_score}
        - **Empathy Score:** {empathy_score}

        **Reasoning:**
        - **Cultivating Change Talk Reasoning:** {cultivating_change_talk_reasoning}
        - **Softening Sustain Talk Reasoning:** {softening_sustain_talk_reasoning}
        - **Partnership Reasoning:** {partnership_reasoning}
        - **Empathy Reasoning:** {empathy_reasoning}

        **Behavior Code Counts:**
        - **CR Count:** {cr_count}
        - **SR Count:** {sr_count}
        - **Q Count:** {q_count}
        - **GI Count:** {gi_count}
        - **Persuade Count:** {persuade_count}
        - **Persuade with Count:** {persuade_with_count}
        - **AF Count:** {af_count}
        - **Seek Count:** {seek_count}
        - **Emphasize Count:** {emphasize_count}
        - **Confront Count:** {confront_count}

        **Behavior Code Percentages:**
        - **Percent CR:** {percent_cr}%
        - **Reflect Question Ratio:** {reflect_question_ratio}
        - **Total MI Adherent:** {total_mi_adherent}
        - **Total MI Non-Adherent:** {total_mi_non_adherent}

        **Technical Global Score:** {technical_global}
        **Relational Global Score:** {relational_global}

        **Counseling Transcript:**
        {self.conversation_history}

        **MITI 4.2.1 Coding Manual:**
        {self.miti_manual}

        Output:
        <Insert your summary here>
        """

        response = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=max_tokens
        )

        response_text = response.choices[0].message.content

        # Your dictionary
        summary_data = {
            "Overall Summary & Recommendations": response_text,
            "Data & Stats Summary": { 
                "Cultivating Change Talk Score": cultivating_change_talk_score,
                "Softening Sustain Talk Score": softening_sustain_talk_score,
                "Partnership Score": partnership_score,
                "Empathy Score": empathy_score,
                "Cultivating Change Talk Reasoning": cultivating_change_talk_reasoning,
                "Softening Sustain Talk Reasoning": softening_sustain_talk_reasoning,
                "Partnership Reasoning": partnership_reasoning,
                "Empathy Reasoning": empathy_reasoning,
                "CR Count": cr_count,
                "SR Count": sr_count,
                "Q Count": q_count,
                "GI Count": gi_count,
                "Persuade Count": persuade_count,
                "Persuade with Count": persuade_with_count,
                "AF Count": af_count,
                "Seek Count": seek_count,
                "Emphasize Count": emphasize_count,
                "Confront Count": confront_count,
                "Percent CR": percent_cr,
                "Reflect Question Ratio": reflect_question_ratio,
                "Total MI Adherent": total_mi_adherent,
                "Total MI Non-Adherent": total_mi_non_adherent,
                "Technical Global Score": technical_global,
                "Relational Global Score": relational_global
            }
        }

        # Convert to JSON string
        summary_json_string = json.dumps(summary_data, indent=4)

        # Update the summary DataFrame
        new_row = {
            'session_id': session_id,
            'summary': summary_json_string
        }

        new_row_df = pd.DataFrame([new_row])
        summary_data_frame = pd.concat([summary_data_frame, new_row_df], ignore_index=True)
        
    def add_data(self, session_id, dialogue_turn, speaker, text_response, implicit_biases, executive_function, metacognition, miti_behavior_codes, reasoning):
        """
        Adds a new row of data to the DataFrame.
        """
        global full_data_frame
        new_row = {
            'session_id': session_id,
            'dialogue_turn': dialogue_turn,
            'speaker': speaker,
            'text_response': text_response,
            'patient_implicit_biases': implicit_biases,
            'patient_executive_function': executive_function,
            'patient_metacognition': metacognition,
            'miti_behavior_codes': miti_behavior_codes,
            'reasoning': reasoning
        }

        new_row_df = pd.DataFrame([new_row])
        full_data_frame = pd.concat([full_data_frame, new_row_df], ignore_index=True)
    
    def save_full_data_frame(self, filename='full_data_frame.csv'):
        """
        Saves the DataFrame to a CSV file.
        """
        full_data_frame.to_csv(filename, index=False)

    def save_summary_data_frame(self, filename='summary_data_frame.csv'):
        """
        Saves the Summary DataFrame to a CSV file.
        """
        summary_data_frame.to_csv(filename, index=False)

if __name__ == "__main__":
    patient = SimulatedPatient()

    session_id = 1
    count = 1
    while True:
        user_input = input("Enter your message (or 'quit' to stop): ")
        if user_input.lower() == 'quit':
            break
        
        metrics = patient._generate_temp_evaluation_metrics(user_input)

        patient.add_data(session_id, count, "therapist", user_input, patient.implicit_biases, patient.executive_function, patient.metacognition, metrics["behavior_codes"], metrics["reasoning"])
        
        count += 1
        response = patient._generate_natural_language_response(user_input)
        patient._update_cognitive_model(response)
        print(response)

        patient.add_data(session_id, count, "patient", response, patient.implicit_biases, patient.executive_function, patient.metacognition, ["None"], "None")
        
        count += 1

    patient.save_full_data_frame()
    patient._generate_session_summary(session_id)
    patient.save_summary_data_frame()
