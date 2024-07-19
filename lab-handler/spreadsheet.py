import os

from fastapi import FastAPI, HTTPException

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config_handler import ConfigHandler

class SpreadsheetHandler:

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    def __init__(self, spreadsheet_id : str):
        self._spreadsheet_id = spreadsheet_id
    
    def get_sheets_service(self):
        credentials = None
        if os.path.exists("token.json"):
            credentials = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.SCOPES)
                credentials = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(credentials.to_json())
        
        try:
            service = build("sheets", "v4", credentials=credentials)
            sheets = service.spreadsheets()
            return sheets
        except:
            pass
    
    def get_sheet_names(self):
        service = self.get_sheets_service()
        sheet_metadata = service.get(spreadsheetId=self._spreadsheet_id).execute()
        metas = sheet_metadata.get('sheets', '')
        names = [item.get('properties', '').get('title', '') for item in metas]
        return names
    

    def get_range(self, sheetname:str, range : str):
        sheets = self.get_sheets_service()
        request_str = sheetname + "!" + range
        result = sheets.values().get(spreadsheetId = self._spreadsheet_id, range=request_str).execute()
        result = result.get("values", [])
        return result
    
    def number_to_column_letter(self, n):
        result = ""
        n += 1
        while n > 0:
            n, remainder = divmod(n - 1, 26)
            result = chr(65 + remainder) + result
        return result
    
    def number_to_row_id(self, n):
        return n + 1

    def find_column_id(self, sheetname:str, column_name:str):
        try:
            row = self.get_range(sheetname, "1:1")[0]
            index = row.index(column_name)
            return index
        except ValueError:
            raise HTTPException(status_code=404, detail="Колонка не найдена")
    
    def find_student_row_id(self, sheetname:str, student_column_id : int, student_name:str):
        try:
            student_column_id = self.number_to_column_letter(student_column_id)
            column = self.get_range(sheetname, student_column_id + ":" + student_column_id)
            flat_list = [item for sublist in column for item in sublist]
            return flat_list.index(student_name)
        except:
            raise HTTPException(status_code=404, detail="Студент не найден")
    
    def print_range(self, sheetname:str, range : str, values : list):
        sheets = self.get_sheets_service()
        request_str = sheetname + "!" + range
        sheets.values().update(spreadsheetId = self._spreadsheet_id, range=request_str, valueInputOption="USER_ENTERED", body={'values' : values}).execute()
    
    def get_lab_column_id(self, sheetname: str, lab_name:str):
        try:
            row = self.get_range(sheetname, "2:2")[0]
            index = row.index(lab_name)
            return index
        except ValueError:
            raise HTTPException(status_code=404, detail="Лабораторная не найдена")

    def get_lab_deadline(self, sheetname :str, lab_name: str):
        column_id = self.get_lab_column_id(sheetname, lab_name)
        request_str = sheetname + "!" + self.number_to_column_letter(column_id) + "1"
        sheets = self.get_sheets_service()
        result = sheets.values().get(spreadsheetId = self._spreadsheet_id, range=request_str).execute()
        result = result.get("values", [])
        return result[0][0]
    
    def print_mark(self, sheetname:str, lab_name: str, github_login: str, mark : str):
        github_column_id = self.find_column_id(sheetname, "GitHub")
        github_column_id_str = self.number_to_column_letter(github_column_id)

        sheets = self.get_sheets_service()
        github_column = self.get_range(sheetname, github_column_id_str + ":" + github_column_id_str)
        print(github_column)
        flat_list = [item for sublist in github_column for item in (sublist if sublist else [''])]
        print(flat_list)
        student_row_id = flat_list.index(github_login)
        studen_row_id_str = self.number_to_row_id(student_row_id)
        print(student_row_id)
        lab_column_id = self.get_lab_column_id(sheetname, lab_name)
        lab_column_id_str = self.number_to_column_letter(lab_column_id)
        print(lab_column_id_str + str(studen_row_id_str))
        old = self.get_range(sheetname, lab_column_id_str + str(studen_row_id_str))
        if not old:
            self.print_range(sheetname, lab_column_id_str + str(studen_row_id_str), [[mark]])
        else:
            raise HTTPException(status_code=409, detail= "Проверка лабораторной работы уже была пройдена ранее. Для повторной проверки обратитесь к преподавателю")