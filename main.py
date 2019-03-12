import psycopg2
import httplib2
import apiclient
from oauth2client.service_account import ServiceAccountCredentials

DB_SETTINGS = {
    'HOST': 'localhost',
    'DB_NAME': 'test_base',
    'USER_NAME': 'postgres',
    'PASSWORD': 'qwerty1234',
    'QUERY': """SELECT * 
                FROM tabletoexport.testtable""",
}

GOOGLE_SETTINGS = {
    'SHEET_ID': 'your_sheet_id',
    'CREDENTIALS_FILE': 'yourproject.json',  # имя файла с закрытым ключом
    'start_cell': 'A2'
}

# достаем данные из БД:
data_for_google_sheet = []
with psycopg2.connect(dbname=DB_SETTINGS['DB_NAME'], user=DB_SETTINGS['USER_NAME'],
                      password=DB_SETTINGS['PASSWORD'], host=DB_SETTINGS['HOST']) as conn:
    with conn.cursor(cursor_factory=None) as cursor:
        cursor.execute(DB_SETTINGS['QUERY'])
        for row in cursor:
            data_for_google_sheet.append(list(map(str, row)))


# подключаемся к Google-табличке и вставляем собранные из БД данные:
credentials = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SETTINGS['CREDENTIALS_FILE'],
                                                               ['https://www.googleapis.com/auth/spreadsheets',
                                                                'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

batch_update_values_request_body = {
    'value_input_option': 'USER_ENTERED',
    'data': [{
        "range": GOOGLE_SETTINGS['start_cell'],
        "majorDimension": 'ROWS',
        "values": data_for_google_sheet
    }],
}

request = service.spreadsheets().values().batchUpdate(spreadsheetId=GOOGLE_SETTINGS['SHEET_ID'],
                                                      body=batch_update_values_request_body)
response = request.execute()
