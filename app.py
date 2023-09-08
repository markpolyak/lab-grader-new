import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Используем ключ сервисного аккаунта для аутентификации
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('tmpkey.json', scope)
client = gspread.authorize(creds)

# Открываем таблицу по ее имени (название таблицы в URL)
spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/15yVKYIUea6gj2wTWR1ndPzeGENDyBIxo1eHZDkRljUI/edit?pli=1#gid=0')

# Получаем список имен листов
all_sheet_names = [sheet.title for sheet in spreadsheet.worksheets()]

print(all_sheet_names)