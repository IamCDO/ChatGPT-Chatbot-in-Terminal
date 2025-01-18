import sqlite3
import time
import requests
con = sqlite3.connect('Chatgpt.sqlite')
cur = con.cursor()
#cur.execute('DROP TABLE IF EXISTS chat_history')
con.execute('CREATE TABLE IF NOT EXISTS chat_history(user_query TEXT, gpt_response TEXT, time TEXT, query_id INTEGER)')

endpoint = 'https://api.openai.com/v1/chat/completions'
#NOTE: The token used below is a placeholder, you should open a developer account with OpenAI(https://openai.com) in order to get an API key for your self.
token = 'sk-proj-boTWzYpYN_0k8L6LJJrYTjPAnUMEq4XmsCBI7wF1n0Yd3Jy1J9qa5dS1PZ7lnno9IAAih22FwzU9iNpQTUoIHFqCCyLlSZnUy_eXJLrVTbiyBxvhTwQA'
header = {'Authorization':f'BEARER {token}'}
end = ''
        
while end.lower() != 'quit':
    user_query = input('What would you like me to help you with?\n')
    cur.execute('SELECT user_query, query_id FROM chat_history ORDER BY query_id')
    hist = [(uquery,q_id) for uquery, q_id in cur]
    last_query = hist[len(hist)-1][0]#This represents the last query that was added to the database.
    previous_query = hist[len(hist)-2][0]#This represents the pen-ultimate(i.e second to the last) query that was added to the database.
    data = {"model":"gpt-4o-mini","messages":[
        {"role":"system","content":"You are an AI assistant that gives explicit answers to users requests"},
        {"role":"user","content":f'''For context, here are the last and previous questions that I asked you respectively {last_query}, and 
        {previous_query}, here is my current query which you should provide an answer to {user_query}, using my previous queries for context if
        needed'''}]}#I used the triple quote because I wanted to break my 'f-string' line into different lines, rather than write that in only
        #one line, if I had used the single or double quotes, I would have gotten errors saying the initial(f-string)line of code was not closed.
        #This will enable the chatbot have access too the last two queries of the user in order to enable it reference the users past
        #questions for better context, I will also try to make it have access to more past searches in order to make it have better context when
        #answering new questions related to old ones.
    print(id(data))
    response = requests.post(endpoint, headers= header, json=data)
    cur.execute('SELECT query_id FROM chat_history ORDER BY query_id')
    ID = [ids for ids in cur]#This appends all the values under every row in the 'query_id' column to the list assigned to the variable 'ID'
    print(ID)
    if len(ID) >= 1: 
        query_id = ID[len(ID)-1][0]#This will select the element with index 0 in the last tuple(ID[len(ID)-1]) in the list, since this
        #will be the last ID that was added to the database.        
    else:
        query_id = 0
    print('This is the id of the last query by the user:', query_id)
    if response.status_code == 200:
        ai_response = response.json()['choices'][0]['message']['content'].rstrip()
        print(ai_response)
        cur.execute('INSERT INTO chat_history(user_query, gpt_response, time, query_id) VALUES(?,?,?,?)',(user_query,ai_response,time.ctime(),query_id + 1))
        con.commit()
    else:
        print(f'Error {response.status_code} occured:')
        print(response.json()['error']['message'])
    print('')#This is to create a blank line
    end = input('If you would like to end the session, type in quit\n')
cur.execute('SELECT * FROM chat_history ORDER BY query_id')
chathistory = [(query, resp, date, ids) for query, resp, date, ids in cur]
for query, resp, date, ids in chathistory:
    print(f'{date}, QUERY-ID: {ids}\nUSER-QUERY: {query}\nAI-RESPONSE: {resp}\n')
        
