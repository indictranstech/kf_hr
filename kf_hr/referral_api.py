from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
import json
from frappe.utils.user import get_user_fullname
import requests
from frappe.utils import cint, cstr, flt, formatdate, getdate, now, today


# #login API
@frappe.whitelist(allow_guest=True)
def login_api(data=None):
	data = json.loads(frappe.request.data)
	url = "http://hr.kfcommunity.com/api/method/login"
	username = data.get("username")
	password = data.get("password")
	# return username, password
	response=requests.post(url, data={"usr":username, "pwd":password})
	if response.status_code == 200:
		response_text = json.loads(response.text)
		user = frappe.db.get_value("User", {"Username":data.get("username")}, "name")
		roles = frappe.get_roles(user)
		emp = frappe.db.get_values("KF Employee Master", {"user_id":user}, ["department", "branch", 'name'])
		response_text["roles"] = roles
		response_text["department"] = emp[0][0] if emp else ""
		response_text["branch"] = emp[0][1] if emp else ""
		response_text["employee_id"] = emp[0][2] if emp else ""
		response_text["username"] = data.get("username")
		response_text["email"] = user
		return {"status_code":200, "success":True, "error":"", "data":response_text}
		# return response_text
	else:
		return {"status_code":401, "success":False, "error":"Invalid Username or Password"}



@frappe.whitelist(allow_guest=True)
def create_referral_form():
	data = json.loads(frappe.request.data)
	try:
		referral_form = frappe.new_doc("Referral Form")
		referral_form.workflow_state = "Pending"
		referral_form.date = today()
		referral_form.employee = data.get("employee")
		referral_form.employee_name = data.get("employee_name")
		referral_form.email_id = data.get("email_id")
		referral_form.department_name = data.get("department_name")
		referral_form.branch_name = data.get("branch_name")
		referral_form.referral_employee = data.get("referral_employee")
		referral_form.referral_employee_name = data.get("referral_employee_name")
		referral_form.ref_email_id = data.get("ref_email_id")
		referral_form.referral_department = data.get("referral_department")
		referral_form.referral_branch = data.get("referral_branch")
		referral_form.referral_remarks = data.get("referral_remarks")
		referral_form.client_name = data.get("client_name")
		referral_form.mobile_number = data.get("mobile_number")
		referral_form.client_email_id = data.get("client_email_id")
		referral_form.amount = data.get("amount")
		referral_form.client_description = data.get("client_description")
		referral_form.flags.ignore_mandatory = True
		referral_form.save(ignore_permissions=True)
		frappe.db.commit()
		return {"status_code":200, "success":True, "error":"", "data":referral_form}
	except Exception as e:
 		return {"status_code":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def update_referral_details(data=None):
	data = json.loads(frappe.request.data)

	try:
		if frappe.db.get_value("Referral Form", {"referral_number":data.get("referral_number")}, "name"):
			referral_form = frappe.get_doc("Referral Form", data.get("referral_number"))
			referral_form.workflow_state = data.get("workflow_state")
			referral_form.reason_of_rejection = data.get("reason_of_rejection")
			referral_form.referral_remarks = data.get("referral_remarks")
			referral_form.referral_employee = data.get("referral_employee")
			referral_form.referral_employee_name = data.get("referral_employee_name")
			referral_form.ref_email_id = data.get("ref_email_id")
			referral_form.referral_department = data.get("referral_department")
			referral_form.referral_branch = data.get("referral_branch")
			referral_form.client_name = data.get("client_name")
			referral_form.client_email_id = data.get("client_email_id")
			referral_form.mobile_number = data.get("mobile_number")
			referral_form.amount = data.get("amount")
			referral_form.save(ignore_permissions=True)
			frappe.db.commit()
			return {"status_code":200, "success":True, "error":"", "data":referral_form}
		else:
			return {"status_code":404, "success":False, "error":"Referral Form Not Found"}
	except Exception as e:
		return {"status_code":401, "success":False, "error":e}


#Get all referral details
@frappe.whitelist(allow_guest=True)
def get_all_referral_form():
	data = json.loads(frappe.request.data)
	try:
		referral_details = frappe.db.sql("""SELECT workflow_state, referral_number, employee, employee_name, email_id, DATE_FORMAT(date,'%d-%m-%Y') as date, department_name, branch_name, referral_employee, referral_employee_name, referral_department, referral_branch, ref_email_id, referral_remarks, client_name, amount, client_email_id, mobile_number, client_description,reason_of_rejection from `tabReferral Form` where (employee like '{0}' or referral_employee like '{0}') and {1} order by modified desc""".format(data.get("employee_id"), get_filters_codition(data)), as_dict=1)
		return {"status_code":200, "success":True, "error":"", "data":referral_details}
	except Exception as e:
		return {"status_code":401, "success":False, "error":e}

def get_filters_codition(data):
        conditions = "1=1"
        if data.get("referral_number"):
            conditions += " and name = '{0}'".format(data.get('referral_number'))
        if data.get("date"):
            conditions += " and date = '{0}'".format(getdate(data.get('date')))
        return conditions


@frappe.whitelist(allow_guest=True)
def user_profile_details(data=None):
	data = json.loads(frappe.request.data)
	user = frappe.db.sql("""SELECT email, first_name, username from `tabUser` where username='{0}'""".format(data.get("username")), as_dict=1) 
	return user[0]


@frappe.whitelist(allow_guest=True)
def employee_details():
	data = json.loads(frappe.request.data)
	try:
		emp = frappe.db.sql("""SELECT name as employee_id, employee_name, department, branch, user_id as email From `tabKF Employee Master` where status='Active' and name='{0}' """.format(data.get("employee")), as_dict=1)
		# return emp[0] if emp else ""
		return {"status_code":200, "success":True, "error":"", "data":emp[0] if emp else ""}
	except Exception as e:
		return {"status_code":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def referral_from_list():
	data = json.loads(frappe.request.data)
	offset = (cint(data.get("limit"))*cint(data.get("offSet"))) - cint(data.get("limit"))
	# if offset < 0 or data.get("name"):
	# 	offset = 0

	try:
		referral_form = frappe.db.sql("""SELECT referral_number, workflow_state, employee_name, department_name, DATE_FORMAT(date,'%d-%m-%Y') as date, client_name From `tabReferral Form` where (employee like '{0}' or referral_employee like '{0}') and {1} order by modified desc limit {2} offSet {3} """.format(data.get("employee_id"), referral_form_list_filters_codition(data),cint(data.get("limit")), offset), as_dict=1)
		# if not referral_form:
		# 	referral_form = frappe.db.sql("""SELECT referral_number, workflow_state, employee_name, department_name, date From `tabReferral Form` where (employee like '{0}' or referral_employee like '{0}') and {1} order by name DESC limit {2} """.format(data.get("employee_id"), referral_form_list_filters_codition(data),cint(data.get("limit")), offset), as_dict=1)
		
		total_records = len(frappe.db.sql("""SELECT name From `tabReferral Form` where (employee like '{0}' or referral_employee like '{0}')""".format(data.get("employee_id")), as_dict=1))
		return {"status_code":200, "success":True, "error":"", "total_records":total_records, "data":referral_form}
	except Exception as e:
		return {"status":401, "success":False, "error":e}


def referral_form_list_filters_codition(data):
        conditions = "1=1"
        if data.get("workflow_state"):
            conditions += " and workflow_state = '{0}'".format(data.get('status'))
        if data.get("department_name"):
            conditions += " and department_name = '{0}'".format(data.get('department_name'))
        return conditions

@frappe.whitelist(allow_guest=True)
def employee_list_api():
	data=json.loads(frappe.request.data)
	emp = '%'+data.get("employee")+'%'
	try:
		employee = frappe.db.sql("""SELECT name as employee_id, employee_name From `tabKF Employee Master` where status='Active' and relieving_date IS NULL and (name like '{0}' or employee_name like '{0}') """.format(emp), as_dict=1)
		return {"status_code":200, "success":True, "error":"", "data":employee}		
	except Exception as e:
		return {"status":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def department_list():
	try:
		department_list = frappe.db.sql(""" SELECT name as department From `tabDepartment` """, as_dict=1)
		return {"status_code":200, "success":True, "error":"", "data":department_list}
	except Exception as e:
		return {"status":401, "success":False, "error":e}	

@frappe.whitelist(allow_guest=True)
def branch_list():
	try:
		branch_list = frappe.db.sql(""" SELECT name as branch From `tabBranch` """, as_dict=1)
		return {"status_code":200, "success":True, "error":"", "data":branch_list}
	except Exception as e:
		return {"status":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def employee():
	try:
		employee = frappe.db.sql(""" SELECT name as employee_id From `tabKF Employee Master` """, as_dict=1)
		return {"status_code":200, "success":True, "error":"", "data":employee}
	except Exception as e:
		return {"status":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def sent_referral_from():
	data = json.loads(frappe.request.data)
	offset = (cint(data.get("limit"))*cint(data.get("offSet"))) - cint(data.get("limit"))
	search = '%'+data.get("search")+'%'
	try:
		referral_form = frappe.db.sql("""SELECT referral_number, workflow_state, employee_name, department_name, DATE_FORMAT(date,'%d-%m-%Y') as date, client_name, referral_employee_name From `tabReferral Form` where employee='{0}' and (referral_employee like '{1}' or referral_employee_name like '{1}' or client_name like '{1}') order by modified desc limit {2} offSet {3} """.format(data.get("employee_id"), search,cint(data.get("limit")), offset), as_dict=1)
		
		total_records = len(frappe.db.sql("""SELECT name From `tabReferral Form` where employee='{0}' """.format(data.get("employee_id")), as_dict=1))
		return {"status_code":200, "success":True, "error":"", "total_records":total_records, "data":referral_form}
	except Exception as e:
		return {"status":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def received_referral_form():
	data = json.loads(frappe.request.data)
	offset = (cint(data.get("limit"))*cint(data.get("offSet"))) - cint(data.get("limit"))
	search = '%'+data.get("search")+'%'
	try:
		referral_form = frappe.db.sql("""SELECT referral_number, workflow_state, employee_name, department_name, DATE_FORMAT(date,'%d-%m-%Y') as date, client_name From `tabReferral Form` where workflow_state="Pending" and referral_employee='{0}' and (employee like '{1}' or employee_name like '{1}' or client_name like '{1}') order by modified desc limit {2} offSet {3} """.format(data.get("employee_id"), search,cint(data.get("limit")), offset), as_dict=1)

		total_records = len(frappe.db.sql("""SELECT name From `tabReferral Form` where workflow_state="Pending" and referral_employee='{0}'""".format(data.get("employee_id")), as_dict=1))
		return {"status_code":200, "success":True, "error":"", "total_records":total_records, "data":referral_form}
	except Exception as e:
		return {"status":401, "success":False, "error":e}



@frappe.whitelist(allow_guest=True)
def process_referral_form():
	data = json.loads(frappe.request.data)
	offset = (cint(data.get("limit"))*cint(data.get("offSet"))) - cint(data.get("limit"))
	search = '%'+data.get("search")+'%'
	try:
		referral_form = frappe.db.sql("""SELECT referral_number, workflow_state, employee_name, department_name, DATE_FORMAT(date,'%d-%m-%Y') as date, client_name From `tabReferral Form` where (workflow_state="Approved" or workflow_state="Rejected") and referral_employee='{0}' and (employee like '{1}' or employee_name like '{1}' or client_name like '{1}') order by modified desc limit {2} offSet {3} """.format(data.get("employee_id"), search, cint(data.get("limit")), offset), as_dict=1)
		total_records = len(frappe.db.sql("""SELECT name From `tabReferral Form` where (workflow_state="Approved" or workflow_state="Rejected") and referral_employee='{0}' """.format(data.get("employee_id")), as_dict=1))
		return {"status_code":200, "success":True, "error":"", "total_records":total_records, "data":referral_form}
	except Exception as e:
		return {"status":401, "success":False, "error":e}




#Registration APIs
#@frappe.whitelist(allow_guest=True)
#def user_registration_api(data=None):
#	from frappe.model.naming import make_autoname
#	data = json.loads(frappe.request.data)
#	try:
#		user = frappe.new_doc("User")
#		user.email = data.get("email")
#		user.first_name = data.get("name")
#		user.new_password = data.get("password")
#		user.send_password_update_notification = 0
#		user.send_welcome_email=0
#		user.mobile_no = data.get("phone_number")
#		user.append('roles',{
#			"doctype": "Has Role",
#			"role":"Referral User"
#		})
#		user.save(ignore_permissions=True)
#		frappe.db.commit()

		# frappe.get_doc({
		# 	"doctype": "Employee",
		# 	"salutation": "Mr",
		# 	"employee_name": data.get("name"),
		# 	"user_id": data.get("email"),
		# 	"date_of_birth": "1994-03-15",
		# 	"date_of_joining": today(),
		# 	"gender": "Male",
		# 	"branch": "Mumbai",
		# 	"department": "Finance",
		# 	"sub_cost_center": "Finance",
		# 	"designation": "Vice President - Finance",
		# 	"employment_mode": "Payroll"
		# }).insert(ignore_permissions=True)
		#nm = make_autoname(data.get("name")+".####")

#		return {"status_code":200, "success":True, "error":"", "data":user}
#	except Exception as e:
#		return {"status":401, "success":False, "error":e}
