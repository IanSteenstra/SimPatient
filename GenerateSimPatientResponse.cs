using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Xml;
using Jint.Native;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.Networking;

public class GenerateSimPatientResponse : MonoBehaviour
{
    [Serializable]
    private class SimPatientResponse
    {
        public string id;
        [JsonProperty("object")]
        public string created;
        public string model;
        public string system_fingerprint;
        public List<SimPatientChoice> choices;
        public Usage usage;
    }

    [Serializable]
    private class SimPatientChoice
    {
        public int index;
        public Message message;
        public object logprobs;
        public string finish_reason;
    }

    [Serializable]
    private class Message
    {
        public string role;
        public string content;
    }

    [Serializable]
    private class Usage
    {
        public int prompt_tokens;
        public int completion_tokens;
        public int total_tokens;
    }

    [Serializable]
    private class RequestData
    {
        public string model;
        public int max_tokens;
        public int temperature;
        public Dictionary<string, string> response_format;
        public List<ChatMessage> messages = new List<ChatMessage>();
    }

    [Serializable]
    private class ChatMessage
    {
        public string role;
        public string content;
    }
    
    [Serializable]
    private class SimPatientResponseOutput
    {
        public string patient_response;
        public int non_verbal_cue_number;
    }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    private static void Initialize()
    {
        var generateSimPatientResponse = new GameObject("GenerateSimPatientResponse").AddComponent<GenerateSimPatientResponse>();
        Globals.Register(generateSimPatientResponse);
    }

    public void StartSimPatientResponseCoroutine(Delegate callback)
    {
        Debug.Log("StartSimPatientResponseCoroutine");
        StartCoroutine(SimPatientResponseAsync(callback));
    }

    private IEnumerator SimPatientResponseAsync(Delegate callback)
    {
        string openAIUrl = "https://api.openai.com/v1/chat/completions";
        string openAIAuthorization = Environment.GetEnvironmentVariable("OPENAI_AUTHORIZATION");

        var requestData = new RequestData
        {
            model = GetVariable("LLM_MODEL"),
            max_tokens = 64,
            temperature = 1,
            response_format = new Dictionary<string, string> { { "type", "json_object" } }
        };

        string user_input = "'" + GetVariable("USER_INPUT").Replace("\n", "").Replace("\t", "").Replace("\r", "").Replace("'", "").Replace("\"", "").Replace("’", "").Replace("‘", "").Replace(
                "“", "").Replace("”", "").Replace(",", "") + "'";

        SetVariable("USER_INPUT", user_input);

        int session_id = GetAsInt("SESSION_ID"); 

        // Retrieve SESSION_HISTORY and convert it to a list
        string sessionHistory= GetVariable("SESSION_HISTORY");
        sessionHistory += $"user|{user_input}||";

        var generateSimPatientResponsePrompt = 
            "You are simulating a patient struggling with alcohol misuse, interacting with a counselor. Your responses should reflect the underlying cognitive processes of this individual, without explicitly mentioning these processes or numerical scores. Also, subtly personify the persona attributes/characteristics of the patient in your responses without explicitly stating them to the counselor.\n\n" +
            "**Persona Attributes:**\n" +
            $"- ** Gender: {GetVariable("GENDER")}\n" +
            $"- ** Ethnicity: {GetVariable("ETHNICITY")}\n" +
            $"- ** Age: {GetVariable("AGE")}\n" +
            $"- ** Occupation: {GetVariable("OCCUPATION")}\n" +
            $"- ** MBTI Personality Type: {GetVariable("MBTI")}\n" +
                "    - Explanation: Your MBTI personality type based on the following dimensions:\n" +
                "        - Introverted (I) vs. Extraverted (E):\n" +
                "            - Introverted individuals prefer solitary activities and get exhausted by social interaction. They tend to be quite sensitive to external stimulation (e.g. sound, sight or smell) in general.\n" +
                "            - Extraverted individuals prefer group activities and get energized by social interaction. They tend to be more enthusiastic and more easily excited than Introverts.\n" +
                "        - Observant (S) vs. Intuitive (N):\n" +
                "            - Observant individuals are highly practical, pragmatic and down-to-earth. They tend to have strong habits and focus on what is happening or has already happened.\n" +
                "            - Intuitive individuals are very imaginative, open-minded and curious. They prefer novelty over stability and focus on hidden meanings and future possibilities.\n" +
                "        - Thinking (T) vs. Feeling (F):\n" +
                "            - Thinking individuals focus on objectivity and rationality, prioritizing logic over emotions. They tend to hide their feelings and see efficiency as more important than cooperation.\n" +
                "            - Feeling individuals are sensitive and emotionally expressive. They are more empathic and less competitive than Thinking types, and focus on social harmony and cooperation.\n" +
                "        - Judging (J) vs. Prospecting (P):\n" +
                "            - Judging individuals are decisive, thorough and highly organized. They value clarity, predictability and closure, preferring structure and planning to spontaneity.\n" +
                "            - Prospecting individuals are very good at improvising and spotting opportunities. They tend to be flexible, relaxed nonconformists who prefer keeping their options open.\n" +
                "        - Assertive (A) vs. Turbulent (T):\n" +
                "            - Assertive individuals are self-assured, even-tempered and resistant to stress. They refuse to worry too much and do not push themselves too hard when it comes to achieving goals.\n" +
                "            - Turbulent individuals are self-conscious and sensitive to stress. They are likely to experience a wide range of emotions and to be success-driven, perfectionistic and eager to improve.\n" +
            $"- ** Control Level: {GetVariable("PATIENT_CONTROL")}\n" +
            "    - Explanation: Your level of ability to regulate your own thoughts, emotions, and actions (1-10 scale).\n" +
            "    - High Levels (Example Score: 10): \"I'm pretty good at controlling myself. I don't really have a problem saying no to a drink.\"\n" +
            "    - Low Levels (Example Score: 1): \"I just can't seem to stop myself once I start drinking. It's like something takes over.\"\n" +
            $"- ** Self-Efficacy Level: {GetVariable("PATIENT_EFFICACY")}\n" +
            "    - Explanation: Your level of confidence in your ability to resist cravings, cope with triggers, and achieve your recovery goals. (1-10 scale)\n" +
            "    - High Levels (Example Score: 10): \"I'm confident I can handle any situation without needing alcohol. I've got this.\"\n" +
            "    - Low Levels (Example Score: 1): \"I don't think I can do this. Alcohol has such a hold on me, I always go back to it.\"\n" +
            $"- ** Awareness Level: {GetVariable("PATIENT_AWARENESS")}\n" +
            "    - Explanation: Your level of ability to accurately perceive and evaluate your own thoughts, feelings, and behaviors. (1-10 scale)\n" +
            "    - High Levels (Example Score: 10): \"I'm completely aware of the effects alcohol has on me and how it impacts my life.\"\n" +
            "    - Low Levels (Example Score: 1): \"I don't really see what the big deal is. I can stop drinking anytime I want.\"\n" +
            $"- ** Reward Level: {GetVariable("PATIENT_REWARD")}\n" +
            "    - Explanation: The level in which alcohol and its cues trigger cravings and automatic behaviors in you. (1-10 scale)\n" +
            "    - High Levels (Example Score: 10): \"Honestly, just the smell of beer makes me crave a cold one. It's instant relaxation.\"\n" +
            "    - Low Levels (Example Score: 1): \"Alcohol doesn't really do much for me anymore. It just makes me feel sick.\"\n\n" +
            "**Additionally, you may include one, and only one, in-line non-verbal cue in your response to subtly reflect your cognitive state. You will choose the cue you want by providing the number associated with it. For example, you might say \"I'm fine\" while avoiding eye contact via including <gaze dir=\"AWAY\" />, indicating that you are not fine. In that case, your output should be in a JSON format of your response ('patient_response') without the non-verbal cue, and the non-verbal cue number ('non_verbal_cue_number') of 1. You don't always have to provide a non-verbal cue, in that case, provide a 0 indicating no non-verbal behavior. Below are some examples of non-verbal cues you can use:\n" +
            "- ** Nothing: [0] No non-verbal behavior\n" +
            "- ** Gaze: [1] <gaze dir=\"AWAY\"/>, [2] <gaze dir=\"TOWARDS\"/>\n" +
            "- ** Expression: [3] <expression type=\"HAPPY\"/>, [4] <expression type=\"NEUTRAL\"/>, [5] <expression type=\"CONCERN\"/>\n" +
            "- ** Eyebrows: [6] <eyebrows dir=\"UP\"/>, [7] <eyebrows dir=\"DOWN\"/>, [8] <eyebrows dir=\"NEUTRAL\"/>\n" +
            "- ** Gesture: [9] <gesture hand=\"L\" cmd=\"THUMBS_UP\"/>, [10] <gesture hand=\"L\" cmd=\"WAVE\"/>\n" +
            "- ** Headnod: [11] <headnod/>\n" +
            "- ** Posture: [12] <posture/>\n\n" +
            (session_id == 1 ? "" : 
            "\nIn addition, you have already had a session with this counselor. Below is the conversation history from your most recent past session as well as an event that you experienced between now and your previous session.\n" +
            $"- Past Session History: {GetVariable("PAST_SESSION_HISTORY")}\n" +
            $"- Between Session Event: {GetVariable("BETWEEN_SESSION_EVENT")}\n") +
            "\nHere's the conversation history so far this session:\n" +
            $"Current Session History: {sessionHistory}\n\n" +
            "Respond to the counselor naturally with just your message. Keep the response short and under 64 tokens.\n\n" +
            $"Counselor: {user_input}\n" +
            "Your JSON Output: {\"patient_response\": \"Your response string here.\", \"non_verbal_cue_number\": \"<non-verbal cues integer here>\"}";
        
        requestData.messages.Add(new ChatMessage { role = "user", content = generateSimPatientResponsePrompt.ToString() });

        var bodyJsonString = JsonConvert.SerializeObject(requestData);

        using UnityWebRequest client = new UnityWebRequest(openAIUrl, "POST")
        {
            uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(bodyJsonString)),
            downloadHandler = new DownloadHandlerBuffer()
        };

        client.SetRequestHeader("Content-Type", "application/json");
        client.SetRequestHeader("Authorization", "Bearer " + openAIAuthorization);
        yield return client.SendWebRequest();

        if (client.result != UnityWebRequest.Result.Success) {
            Debug.Log(openAIUrl + ": " + client.error);
            callback.DynamicInvoke(new JsString(""), new[] {new JsString("")});
        } else {
            var responseContent = client.downloadHandler.text;
            SimPatientResponse jsonResponse = JsonConvert.DeserializeObject<SimPatientResponse>(responseContent);

            string messageContent = jsonResponse.choices[0].message.content;

            SimPatientResponseOutput simPatientResponseOutput = JsonConvert.DeserializeObject<SimPatientResponseOutput>(messageContent);

            string responseText = "'" + simPatientResponseOutput.patient_response.Replace("\n", "").Replace("\t", "").Replace("\r", "").Replace("'", "").Replace("\"", "").Replace("’", "").Replace("‘", "").Replace(
                "“", "").Replace("”", "") + "'";

            SetVariable("RESPONSE_TEXT", responseText);
            SetVariable("NVB_NUMBER", simPatientResponseOutput.non_verbal_cue_number);

            sessionHistory += $"agent|{responseText}||";

            // Convert the session history list back to a string and store it
            SetVariable("SESSION_HISTORY", sessionHistory);

            if (client == null)
            {
                Debug.LogError("Client is null! Cannot invoke callback.");
                // Handle this error appropriately - maybe yield break;
            } 
            else if (client.downloadHandler == null)
            {
                Debug.LogError("Client.downloadHandler is null! Cannot invoke callback.");
                // Handle this error - maybe yield break;
            }
            else if (string.IsNullOrEmpty(client.downloadHandler.text)) 
            {
                Debug.LogError("Client.downloadHandler.text is null or empty! Cannot invoke callback.");
                // Handle this error - maybe yield break;
            }
            else 
            {
                // **Now it's safe to invoke:**
                callback.DynamicInvoke(new JsString(client.downloadHandler.text),
                                    new[] { new JsString(client.downloadHandler.text) });
            }
        }
    }
    private static void SetVariable(string name, object value)
    {
        Globals.Get<PropertyTable>().Set(name, value.ToString());
    }

    private static string GetVariable(string name)
    {
        return Globals.Get<PropertyTable>().Get(name).Replace(",", "");
    }

    private static int GetAsInt(string input)
    {
        return float.TryParse(GetVariable(input), out float result) ? (int) result : 0;
    }
}