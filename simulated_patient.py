import pandas as pd
import openai
import json.decoder
import os
import random

from collections import Counter
from itertools import chain

# Load the API key from an environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("No OPENAI_API_KEY environment variable set")

openai.api_key = API_KEY

# conversation_history database schema
conversation_history_columns = [
    "user_id",
    "persona_id",
    "session_id",
    "dialogue_turn",
    "speaker",
    "text_response",
    "patient_control",
    "patient_efficacy",
    "patient_awareness",
    "patient_reward",
    "miti_behavior_codes",
    "miti_behavior_reasoning"
]

conversation_history_df = pd.DataFrame(columns=conversation_history_columns)

# eval_summary database schema
eval_summary_columns = [
    "user_id",
    "session_id",
    "summary",
    "gi_count",
    "persuade_count",
    "persuade_with_count",
    "q_count",
    "sr_count",
    "cr_count",
    "af_count",
    "seek_count",
    "emphasize_count",
    "confront_count",
    "empathy_score",
    "partnership_score",
    "cultivating_change_talk_score",
    "softening_sustain_talk_score",
    "technical_global_score",
    "relational_global_score",
    "mi_adherence_percentage",
    "mi_non_adherence_percentage"
]

eval_summary_df = pd.DataFrame(columns=eval_summary_columns)

between_session_event_columns = [
    "user_id",
    "persona_id",
    "session_id",
    "event_description"
]

between_session_event_df = pd.DataFrame(columns=between_session_event_columns)

# persona_characteristics database schema
persona_characteristics_columns = [
    "persona_id",
    "age",
    "gender",
    "occupation",
    "ethnicity",
    "MBTI"
]

persona_characteristics_df = pd.DataFrame(columns=persona_characteristics_columns)

# Example: Adding a row to the persona_characteristics DataFrame
example_persona_characteristics_row = {
    "persona_id": "1",
    "age": 30,
    "gender": "Female",
    "occupation": "Teacher",
    "ethnicity": "Hispanic",
    "MBTI": "INFJ-A"
}

# Convert the row to a DataFrame
example_persona_characteristics_df = pd.DataFrame([example_persona_characteristics_row])

# Append the example row to the persona_characteristics DataFrame
persona_characteristics_df = pd.concat([persona_characteristics_df, example_persona_characteristics_df], ignore_index=True)

behavior_codes_keys = ["GI", "Persuade", "Persuade with", "Q", "SR", "CR", "AF", "Seek", "Emphasize", "Confront"]
non_verbal_cues = ['<gaze dir="AWAY"/>', '<gaze dir="TOWARDS"/>', '<expression type="SMILE"/>', '<expression type="NEUTRAL"/>', '<expression type="CONCERN"/>', '<eyebrows dir="UP"/>', '<eyebrows dir="DOWN"/>', '<eyebrows dir="NEUTRAL"/>', '<flush/>', '<gesture hand="L" cmd="THUMBS_UP"/>', '<gesture hand="L" cmd="WAVE"/>', '<greet/>', '<headbob/>', '<headnod/>', '<idle/>', '<posture/>']

class SimulatedPatient:
    def __init__(self, user_id, persona_id, session_id):
        self.conversation_history_df = conversation_history_df
        self.eval_summary_df = eval_summary_df
        self.between_session_event_df = between_session_event_df
        self.persona_characteristics_df = persona_characteristics_df
        self.non_verbal_cues = non_verbal_cues

        self.llm = openai

        self.persona_id = persona_id
        self.persona = self.get_persona_characteristics()

        self.age = self.persona["age"]
        self.gender = self.persona["gender"]
        self.occupation = self.persona["occupation"]
        self.ethnicity = self.persona["ethnicity"]
        self.mbti = self.persona["MBTI"]

        mi_file_path = 'miti4_2.txt'
        with open(mi_file_path, 'r', encoding='iso-8859-1') as file:
            self.miti_manual = file.read()

        self.user_id = user_id
        self.session_id = session_id

        self.session_history = []
        self.dialogue_turn = 1

        self.patient_control = None
        self.patient_efficacy = None
        self.patient_awareness = None
        self.patient_reward = None
        self.retrieve_patient_data()
    
    def get_persona_characteristics(self):
        return self.persona_characteristics_df[self.persona_characteristics_df["persona_id"] == self.persona_id]

    def retrieve_patient_data(self):
        # Filter the DataFrame for rows with the same user_id and persona_id

        if (conversation_history_df.empty):
            # Randomly initialize the patient variables
            self.patient_control = random.randint(1, 10)
            self.patient_efficacy = random.randint(1, 10)
            self.patient_awareness = random.randint(1, 10)
            self.patient_reward = random.randint(1, 10)

        else:
            filtered_df = conversation_history_df[
                (conversation_history_df['user_id'] == self.user_id) &
                (conversation_history_df['persona_id'] == self.persona_id)
            ]

            if not filtered_df.empty:
                # Sort by session_id and dialogue_turn to get the latest entry
                latest_entry = filtered_df.sort_values(
                    by=['session_id', 'dialogue_turn'],
                    ascending=[False, False]
                ).iloc[0]

                # Retrieve and set the patient variables
                self.patient_control = latest_entry['patient_control']
                self.patient_efficacy = latest_entry['patient_efficacy']
                self.patient_awareness = latest_entry['patient_awareness']
                self.patient_reward = latest_entry['patient_reward']
            
            else:
                # Randomly initialize the patient variables
                self.patient_control = random.randint(1, 10)
                self.patient_efficacy = random.randint(1, 10)
                self.patient_awareness = random.randint(1, 10)
                self.patient_reward = random.randint(1, 10)

    def generate_dialogue(self, user_input):
        # TODO: Provide example sentences for each persona attribute to help the LLM understand the context better

        prompt = f"""You are simulating a patient struggling with alcohol addiction, interacting with a therapist. Your responses should reflect the underlying cognitive processes of this individual, without explicitly mentioning these processes or numerical scores. Also, subtly personify the persona attributes/characteristics of the patient in your responses without explicitly stating them to the therapist.
        
        **Persona Attributes:**
        - ** Gender: {self.gender}
        - ** Ethnicity: {self.ethnicity}
        - ** Age: {self.age}
        - ** Occupation: {self.occupation}
        - ** MBTI Personality Type: {self.mbti}
        - ** Control Level: {self.patient_control}
            - Explanation: Your level of ability to regulate your own thoughts, emotions, and actions (1-10 scale). 
        - ** Self-Efficacy Level: {self.patient_efficacy}
            - Explanation: Your level of confidence in your ability to resist cravings, cope with triggers, and achieve your recovery goals. (1-10 scale)
        - ** Awareness Level: {self.patient_awareness}
            - Explanation: Your level of ability to accurately perceive and evaluate your own thoughts, feelings, and behaviors. (1-10 scale)
        - ** Reward Level: {self.patient_reward}
            - Explanation: The level in which alcohol and its cues trigger cravings and automatic behaviors in you. (1-10 scale)
            
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

        You can only use the following in-line non-verbal cues in your response exactly without any modifications. You can use multiple cues in a single response though, but don't overuse them: {self.non_verbal_cues}

        Here's the conversation so far:
        {self.session_history}

        Respond to the therapist naturally with just your message.

        Therapist: {user_input}
        You: 
        """

        response = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a simulated alcohol patient talking with a therapist."},
                      {"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=100
        )

        response_text = response.choices[0].message.content

        return response_text
    
    def generate_summary(self):
        """
        Generates a summary of the session based on the data collected.
        """
        
        # Filter the DataFrame based on user_id and session_id
        filtered_df = conversation_history_df[(conversation_history_df['user_id'] == self.user_id) & 
                                            (conversation_history_df['session_id'] == self.session_id)]
        
        # Extract the miti_behavior_codes column and flatten the list of lists
        miti_behavior_codes = list(chain.from_iterable(filtered_df['miti_behavior_codes']))
        

        # Count the occurrences of each behavior code
        behavior_code_counts = Counter(miti_behavior_codes)
        
        # Convert the Counter object to a dictionary
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

            if af_count > 3: # according to the MITI manual, AF should not exceed 3 in a single session based on a 'soft' limit
                af_count = 3
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
        {self.session_history}
        
        **MITI 4.2.1 Coding Manual:**
        {self.miti_manual}
        """

        response = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            temperature=1,
            max_tokens=512,
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
            response_dict = {}
        
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

        conversation_history_str = ""
        for i in range(len(self.conversation_history_df)):
            speaker = self.conversation_history_df.loc[i, "speaker"]
            utterance = self.conversation_history_df.loc[i, "text_response"]
            miti_behavior_codes_in_convo = self.conversation_history_df.loc[i, "miti_behavior_codes"]
            miti_behavior_codes_in_convo_reasoning = self.conversation_history_df.loc[i, "miti_behavior_reasoning"]
            conversation_history_str += f"{speaker.upper()}: {utterance}; MITI Behavior Codes: {miti_behavior_codes_in_convo}; MITI Behavior Code Reasoning: {miti_behavior_codes_in_convo_reasoning}\n"

        prompt = f"""
        **Summary of Session**
        You are a motivational interviewing (MI) expert tasked with summarizing the session based on the data collected. Provide a concise summary of the session, highlighting key points, insights, and recommendations for future sessions to help the counselor/trainee improve their MI skills. Use the MITI 4.2.1 Coding Manual to help understand what all the codes mean. You do not have to reference the scores below in your summary, but just provide a general overview of the session based off of them and the conversation history.

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

        **Counseling Transcript with Reasoning for MITI Behavior Encoding (User = Therapist/Participant; SimPatient = Simulated Patient):**
        {self.conversation_history_df}

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
            max_tokens=512
        )

        response_text = response.choices[0].message.content

        # Your dictionary
        new_eval_summary_row = {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "summary": response_text,
            "gi_count": gi_count,
            "persuade_count": persuade_count,
            "persuade_with_count": persuade_with_count,
            "q_count": q_count,
            "sr_count": sr_count,
            "cr_count": cr_count,
            "af_count": af_count,
            "seek_count": seek_count,
            "emphasize_count": emphasize_count,
            "confront_count": confront_count,
            "empathy_score": empathy_score,
            "partnership_score": partnership_score,
            "cultivating_change_talk_score": cultivating_change_talk_score,
            "softening_sustain_talk_score": softening_sustain_talk_score,
            "technical_global_score": technical_global,
            "relational_global_score": relational_global,
            "mi_adherence_percentage": total_mi_adherent,
            "mi_non_adherence_percentage": total_mi_non_adherent
        }

        new_eval_summary_row_df = pd.DataFrame([new_eval_summary_row])
        self.eval_summary_df = pd.concat([self.eval_summary_df, new_eval_summary_row_df], ignore_index=True)
        return
    
    def generate_miti_behavior_codes(self, user_input, prev_response_text):        
        prompt = f"""
        **Motivational Interviewing Behavior Code Classification**
        You are a motivational interviewing (MI) expert tasked with classifying therapist volleys and giving a reason for your encoding based on the Motivational Interviewing Treatment Integrity (MITI) 4.2.1 coding manual.
        
    
        Using the attached text from the MITI 4.2.1 coding manual, classify the following therapist volley by behavior codes and give your reasoning. Pay specific attention to the rules for which choosing the behavior codes.
        You must pick the behavior codes from the following list: {behavior_codes_keys}. You also must generate a response in a JSON format with the following structure:
        {{
            "behavior_codes": ["Behavior Code 1", "Behavior Code 2", ...],
            "reasoning": "Your reasoning for choosing the behavior codes."
        }}

        Previous Patient Utterance: {prev_response_text}
        Therapist Utterance: {user_input}
        
        **MITI 4.2.1 Coding Manual:**
        {self.miti_manual}
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
            response_dict = json.loads(response_text) 
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            print(f"Raw response text: {response_text}")
            # Handle the error appropriately (e.g., exit, use default values)
            return []

        return response_dict
    def update_persona_attribute(self, user_input, response_text):
        # TODO: Provide example sentences for each persona attribute to help the LLM understand the context better

        # Update the simulated patient's characteristics based on the response
        prompt = f"""You are evaluating the current persona characteristics of a simulated patient struggling with alcohol. Based on the patient's responses to the therapist, update the below persona characteristics that are demonstrated in the conversation.
        
        **Persona Characteristics Explanations & Current Scores:**
        - **Current Control Level: {self.patient_control}
            - Explanation: Your level of ability to regulate your own thoughts, emotions, and actions (1-10 scale).
        - **Current Self-Efficacy Level: {self.patient_efficacy}
            - Explanation: Your level of confidence in your ability to resist cravings, cope with triggers, and achieve your recovery goals. (1-10 scale)
        - **Current Awareness Level: {self.patient_awareness}  
            - Explanation: Your level of ability to accurately perceive and evaluate your own thoughts, feelings, and behaviors. (1-10 scale)
        - **Current Reward Level: {self.patient_reward}
            - Explanation: The level in which alcohol and its cues trigger cravings and automatic behaviors in you. (1-10 scale)
        
        Here's the conversation so far:
        {self.session_history}

        Previous Therapist Utterance: {user_input}
        Simulated Patient Utterance: {response_text}

        Output in JSON format:
        {{
            "patient_control": <insert updated value>,
            "patient_efficacy": <insert updated value>,
            "patient_awareness": <insert updated value>,
            "patient_reward": <insert updated value>
        }}
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
            return

        # Update the cognitive model
        self.patient_control = updated_states["patient_control"]
        self.patient_efficacy = updated_states["patient_efficacy"]
        self.patient_awareness = updated_states["patient_awareness"]
        self.patient_reward = updated_states["patient_reward"]

        return
    
    def generate_between_session_event(self):
        # Construct conversation history string 
        conversation_history_str = ""
        for i in range(len(self.conversation_history_df)):
            speaker = self.conversation_history_df.loc[i, "speaker"]
            utterance = self.conversation_history_df.loc[i, "text_response"]
            conversation_history_str += f"{speaker.upper()}: {utterance}\n" 

        # Create the prompt for the LLM
        prompt = f"""
        Simulate a Between-Session Event for an Alcohol Addiction Patient

        ## Patient Profile:
        - **Age:** {self.age}
        - **Gender:** {self.gender}
        - **Occupation:** {self.occupation}
        - **Ethnicity:** {self.ethnicity}
        - **MBTI Personality Type:** {self.mbti}
        - **Control Level ({self.patient_control}/10):** {self.patient_control}/10 represents their ability to regulate thoughts, emotions, and actions related to alcohol. 
        - **Self-Efficacy Level ({self.patient_efficacy}/10):** {self.patient_efficacy}/10 indicates their confidence in resisting cravings and achieving sobriety.
        - **Awareness Level ({self.patient_awareness}/10):** {self.patient_awareness}/10 reflects their understanding of their triggers and behaviors.
        - **Reward Level ({self.patient_reward}/10):** {self.patient_reward}/10 shows how strongly alcohol and its cues trigger cravings. 

        ## Previous Session Conversation:
        {conversation_history_str}

        ## Event Description:
        Based on the patient's profile and the content of their last therapy session, describe a realistic and probable event that could have happened to the patient since then. 

        Consider the following:
        - Did they encounter triggers discussed in therapy? 
        - Did they engage in drinking? If so, how much and under what circumstances?
        - Did they use coping mechanisms discussed in therapy?
        - Did they experience any positive or negative emotions related to their progress?
        - Were there any social interactions that influenced their behavior?

        **Example:**
        The patient, feeling stressed about a deadline at work, considered having a drink to cope but ultimately decided to call a friend for support, as they had discussed in therapy.

        **Output:** 
        <Provide the between-session event description here.>
        """

        response = self.llm.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
            temperature=1,  # Adjust temperature for event creativity
            max_tokens=128  # Adjust for desired event description length
        )

        event_description = response.choices[0].message.content

        # Append the event description to the between_session_event_df DataFrame
        new_event_row = {
            "user_id": self.user_id,
            "persona_id": self.persona_id,
            "session_id": self.session_id,
            "event_description": event_description
        }

        new_event_row_df = pd.DataFrame([new_event_row])
        self.between_session_event_df = pd.concat([self.between_session_event_df, new_event_row_df], ignore_index=True)

        return    
    
    def save_conversation_history(self, user_input, response_text):
        prev_response_text = None
        if self.session_history:
            prev_response_text = self.session_history[-1]
            prev_response_text.get("content", None)
        else:
            prev_response_text = ""

        # Update session history
        self.session_history.append({"role": "user", "content": user_input})
        self.session_history.append({"role": "agent", "content": response_text})

        miti_behavior_encoding = self.generate_miti_behavior_codes(user_input, prev_response_text)

        if miti_behavior_encoding:
            miti_behavior_codes = miti_behavior_encoding["behavior_codes"]
            miti_behavior_reasoning = miti_behavior_encoding["reasoning"]

        # Append the conversation to the conversation_history DataFrame
        new_user_row = {
            "user_id": self.user_id,
            "persona_id": self.persona_id,
            "session_id": self.session_id,
            "dialogue_turn": self.dialogue_turn,
            "speaker": "user",
            "text_response": user_input,
            "patient_control": self.patient_control,
            "patient_efficacy": self.patient_efficacy,
            "patient_awareness": self.patient_awareness,
            "patient_reward": self.patient_reward,
            "miti_behavior_codes": miti_behavior_codes,
            "miti_behavior_reasoning": miti_behavior_reasoning
        }
        self.dialogue_turn += 1  

        self.update_persona_attribute(user_input, response_text)

        new_simpatient_row = {
            "user_id": self.user_id,
            "persona_id": self.persona_id,
            "session_id": self.session_id,
            "dialogue_turn": self.dialogue_turn,
            "speaker": "simpatient",
            "text_response": response_text,
            "patient_control": self.patient_control,
            "patient_efficacy": self.patient_efficacy,
            "patient_awareness": self.patient_awareness,
            "patient_reward": self.patient_reward,
            "miti_behavior_codes": [],
            "miti_behavior_reasoning": ""
        }

        # Convert the row to a DataFrame
        new_conversation_history_df = pd.DataFrame([new_user_row, new_simpatient_row])

        # Append the example row to the persona_characteristics DataFrame
        self.conversation_history_df = pd.concat([self.conversation_history_df, new_conversation_history_df], ignore_index=True)

        self.dialogue_turn += 1
        return self.conversation_history_df 

if __name__ == "__main__":
    user_id="1"
    persona_id="1"
    session_id="1"

    patient = SimulatedPatient(user_id, persona_id, session_id)

    while True:
        user_input = input(f"Participant:\n")
        if user_input.lower() == 'quit': # have a button when pressed to stop the session and create a summary
            patient.generate_summary() 
            break
        if user_input.lower() == 'event': # have a button when pressed to stop the session, create a summary and generate a between session event
            patient.generate_summary()
            patient.generate_between_session_event() 
            break
        
        response = patient.generate_dialogue(user_input)

        print("Patient:\n", response)

        patient.save_conversation_history(user_input, response)
    
    print("Conversation History:\n", patient.conversation_history_df)
    print("Evaluation Summary:\n", patient.eval_summary_df)
    print("Between Session Event:\n", patient.between_session_event_df)
    print("Persona Characteristics:\n", patient.persona_characteristics_df)