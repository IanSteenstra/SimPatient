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

public class GenerateInternalStateResponse : MonoBehaviour
{
    [Serializable]
    private class InternalStateResponse
    {
        public string id;
        [JsonProperty("object")]
        public string created;
        public string model;
        public string system_fingerprint;
        public List<InternalStateChoice> choices;
        public Usage usage;
    }

    [Serializable]
    private class InternalStateChoice
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
    private class InternalStateResponseOutput
    {
        public int patient_control;
        public int patient_efficacy;
        public int patient_awareness;
        public int patient_reward;
        public string reasoning;
    }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    private static void Initialize()
    {
        var generateInternalStateResponse = new GameObject("GenerateInternalStateResponse").AddComponent<GenerateInternalStateResponse>();
        Globals.Register(generateInternalStateResponse);
    }

    public void StartInternalStateResponseCoroutine(Delegate callback)
    {
        Debug.Log("StartInternalStateResponseCoroutine");
        StartCoroutine(InternalStateResponseAsync(callback));
    }

    private IEnumerator InternalStateResponseAsync(Delegate callback)
    {
        string openAIUrl = "https://api.openai.com/v1/chat/completions";
        string openAIAuthorization = Environment.GetEnvironmentVariable("OPENAI_AUTHORIZATION");

        var requestData = new RequestData
        {
            model = GetVariable("LLM_MODEL"),
            max_tokens = 256,
            temperature = 1,
            response_format = new Dictionary<string, string> { { "type", "json_object" } }
        };

        string user_input = GetVariable("USER_INPUT");
        string response_text = GetVariable("RESPONSE_TEXT");

        var generateInternalStateResponsePrompt = 
            "You are evaluating the current persona characteristics of a simulated patient struggling with alcohol. Based on the patient's responses to the counselor, update the below persona characteristics that are demonstrated in the conversation and provide a single overall reasoning for your changes or lack of changes.\n\n" +
            "**Persona Characteristics Explanations & Current Scores:**\n" +
            $"- ** Current Control Level: {GetVariable("PATIENT_CONTROL")}\n" +
            "    - Explanation: Your level of ability to regulate your own thoughts, emotions, and actions (1-10 scale).\n" +
            "    - High Levels (Example Score: 10): \"I'm pretty good at controlling myself. I don't really have a problem saying no to a drink.\"\n" +
            "    - Low Levels (Example Score: 1): \"I just can't seem to stop myself once I start drinking. It's like something takes over.\"\n" +
            $"- ** Current Self-Efficacy Level: {GetVariable("PATIENT_EFFICACY")}\n" +
            "    - Explanation: Your level of confidence in your ability to resist cravings, cope with triggers, and achieve your recovery goals. (1-10 scale)\n" +
            "    - High Levels (Example Score: 10): \"I'm confident I can handle any situation without needing alcohol. I've got this.\"\n" +
            "    - Low Levels (Example Score: 1): \"I don't think I can do this. Alcohol has such a hold on me, I always go back to it.\"\n" +
            $"- ** Current Awareness Level: {GetVariable("PATIENT_AWARENESS")}\n" +
            "    - Explanation: Your level of ability to accurately perceive and evaluate your own thoughts, feelings, and behaviors. (1-10 scale)\n" +
            "    - High Levels (Example Score: 10): \"I'm completely aware of the effects alcohol has on me and how it impacts my life.\"\n" +
            "    - Low Levels (Example Score: 1): \"I don't really see what the big deal is. I can stop drinking anytime I want.\"\n" +
            $"- ** Current Reward Level: {GetVariable("PATIENT_REWARD")}\n" +
            "    - Explanation: The level in which alcohol and its cues trigger cravings and automatic behaviors in you. (1-10 scale)\n" +
            "    - High Levels (Example Score: 10): \"Honestly, just the smell of beer makes me crave a cold one. It's instant relaxation.\"\n" +
            "    - Low Levels (Example Score: 1): \"Alcohol doesn't really do much for me anymore. It just makes me feel sick.\"\n\n" +
            "Here's the conversation history so far this session:\n" +
            $"Current Session History: {GetVariable("SESSION_HISTORY")}\n\n" +
            $"Previous Counselor Utterance: {user_input}\n" +
            $"Simulated Patient Utterance: {response_text}\n\n" +
            "Output in JSON format (Make sure to only provide one reasoning):\n" +
            "{\n" +
            "    \"patient_control\": <insert updated integer value>,\n" +
            "    \"patient_efficacy\": <insert updated integer value>,\n" +
            "    \"patient_awareness\": <insert updated integer value>,\n" +
            "    \"patient_reward\": <insert updated integer value>\n" +
            "    \"reasoning\": \"Your single reasoning for all the updated values.\"\n" +
            "}";

        requestData.messages.Add(new ChatMessage { role = "user", content = generateInternalStateResponsePrompt.ToString() });

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
            InternalStateResponse jsonResponse = JsonConvert.DeserializeObject<InternalStateResponse>(responseContent);

            string messageContent = jsonResponse.choices[0].message.content;

            InternalStateResponseOutput internalStateResponseOutput = JsonConvert.DeserializeObject<InternalStateResponseOutput>(messageContent);

            string patientReasoning = internalStateResponseOutput.reasoning.Replace("\n", "").Replace("\t", "").Replace("\r", "").Replace("'", "").Replace("\"", "").Replace(",", "").Replace("’", "").Replace("‘", "").Replace("“", "").Replace("”", "").Replace(",", "");

            SetVariable("PATIENT_CONTROL", internalStateResponseOutput.patient_control.ToString());
            SetVariable("PATIENT_EFFICACY", internalStateResponseOutput.patient_efficacy.ToString());
            SetVariable("PATIENT_AWARENESS", internalStateResponseOutput.patient_awareness.ToString());
            SetVariable("PATIENT_REWARD", internalStateResponseOutput.patient_reward.ToString());

            int dialogueTurn = GetAsInt("DIALOGUE_TURN");

            // Insert new user response into the conversation history
            string query = $"INSERT INTO conversation_history (user_id, persona_id, session_id, dialogue_turn, speaker, text_response, patient_control, patient_efficacy, patient_awareness, patient_reward, miti_behavior_codes, miti_behavior_reasoning, patient_reasoning) VALUES ({GetAsInt("USER_ID")}, {GetAsInt("PERSONA_ID")}, {GetAsInt("SESSION_ID")}, {dialogueTurn}, 'simpatient', {response_text}, {GetAsInt("PATIENT_CONTROL")}, {GetAsInt("PATIENT_EFFICACY")}, {GetAsInt("PATIENT_AWARENESS")}, {GetAsInt("PATIENT_REWARD")}, '', '', '{patientReasoning}');";

            LitebodyDatabase db = (LitebodyDatabase)Globals.Get<Database>();
            Globals.Get<LitebodyDatabaseSessionManager>().InsertOrUpdate(query);

            int nextDialogueTurn = dialogueTurn + 1;
            SetVariable("DIALOGUE_TURN", nextDialogueTurn.ToString());

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