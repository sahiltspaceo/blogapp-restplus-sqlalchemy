from database import db
from database.models import DentistModel,AppointmentModel
from .utils import (get_lang_json,encrypt,decrypt,find_by_userid)
from . import response

from datetime import time

def dentist_list(iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    response_list = []

    db_obj = DentistModel.query.with_entities(
            DentistModel.iDentistID,DentistModel.vDentistName, DentistModel.tOpenTime, DentistModel.tCloseTime,DentistModel.vAddress).all()
    
    for obj in db_obj:
        obj_dict = {
                'iDentistID' : encrypt(str(obj[0])),
                'vDentistName': obj[1],
                'tOpenTime': time.strftime(obj[2], "%H:%M"),
                'tCloseTime': time.strftime(obj[3], "%H:%M"),
                'vAddress': obj[4]
        }
        response_list.append(obj_dict)
    return response.send_response(200, lang_response['dentist']['dentist_list'], response_list)

def set_appointment(data,iUserID):
    lang_response = get_lang_json(find_by_userid(iUserID).vISOLangCode)

    new_appointment = AppointmentModel(
    	iUserID = iUserID,
    	iFamMemID = decrypt(data['iFamMemID']) if data['iFamMemID'] != "" else None,
    	iDentistID = decrypt(data['iDentistID']),
    	dDateOfAppoint = data['dDateOfAppoint'],
    	tTimeOfAppoint = data['tTimeOfAppoint']
    )
    db.session.add(new_appointment)
    db.session.commit()

    return response.send_response(200, lang_response['dentist']['appointment_created'], data)

