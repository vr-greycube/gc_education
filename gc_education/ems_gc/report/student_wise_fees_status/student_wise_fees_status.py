# Copyright (c) 2022, Greycube and contributors
# For license information, please see license.txt

import frappe
from gc_education.ems_gc.report import csv_to_columns
import pandas


def execute(filters=None):
    columns, data = get_data(filters)
    return columns, data


def get_data(filters):
    data = frappe.db.sql(
        """
	select 
		tfs.academic_year , tfs.academic_term , tfs.program ,
		tf.student , tf.student_name , tf.grand_total , tf.outstanding_amount , 
		tf.grand_total - tf.outstanding_amount paid_amount , 
		tf.branch , tf.cost_center , tsg.batch division , 
        ts.student_mobile_number , tsgs.group_roll_number , ts.g_r_number ,
        tf.posting_date , tf.due_date ,
        tfc.fees_category , tfc.amount , tfc.description 
	from `tabFee Schedule` tfs 
    inner join `tabProgram` tpr on tpr.name = tfs.program
	inner join `tabFee Schedule Student Group` tfssg on tfssg.parent = tfs.name
	inner join `tabStudent Group` tsg on tsg.name = tfssg.student_group 
	inner JOIN tabFees tf on tf.fee_schedule = tfs.name
    inner join `tabFee Component` tfc on tfc.parent = tf.name
    inner join tabStudent ts on ts.name = tf.student
    inner join `tabStudent Group Student` tsgs on tsgs.parent = tsg.name and tsgs.student = ts.name 
    {cond}
    order by tfs.program , tsg.batch , tsgs.group_roll_number
    """.format(
            cond=get_conditions(filters)
        ),
        filters,
        as_dict=True,
    )

    if not data:
        return [], []

    df = pandas.DataFrame.from_records(data)
    df1 = pandas.pivot_table(
        df,
        index=[
            "academic_year",
            "academic_term",
            "program",
            "division",
            "g_r_number",
            "student",
            "student_name",
            "due_date",
            "description",
            "grand_total",
            "paid_amount",
            "outstanding_amount",
        ],
        columns=["fees_category"],
        values=["amount"],
        fill_value=0,
        margins=True,
        margins_name="Total",
        aggfunc="sum",
        dropna=True,
    )
    df1.drop(index="Total", axis=0)
    df1.columns = df1.columns.to_series().str[1]
    df2 = df1.reset_index()

    columns = get_columns()

    pivot_cols = [
        dict(label=col, fieldname=col, fieldtype="Currency", options="", width=140)
        for col in df1.columns.to_list()
        if not col == "Total"
    ]
    columns[9:9] = pivot_cols
    # columns[-1]["label"] = "Total"

    out = []
    for d in df2.to_dict("r"):
        out.append({k: v for k, v in d.items() if v})
    out[-1]["bold"] = 1

    return columns, out


def get_conditions(filters):
    conditions = []
    if filters.get("academic_year"):
        conditions.append(" tfs.academic_year = %(academic_year)s")
    if filters.get("academic_term"):
        conditions.append(" tfs.academic_term = %(academic_term)s")
    if filters.get("batch"):
        lst = filters.batch
        # to prevent SQL Injection
        batches = frappe.get_list("Student Batch Name", pluck="name")
        conditions.append(
            "tsg.batch in ({})".format(
                ",".join(["'%s'" % d for d in lst if d in batches])
            )
        )
    if filters.get("from_date"):
        conditions.append("tf.due_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("tf.due_date <= %(to_date)s")
    if filters.get("program"):
        lst = filters.program
        # to prevent SQL Injection
        programs = frappe.get_list("Program", pluck="name")
        conditions.append(
            "tfs.program in ({})".format(
                ",".join(["'%s'" % d for d in lst if d in programs])
            )
        )
    if filters.get("department"):
        # to prevent SQL Injection
        names = frappe.get_list("Department", pluck="name")
        conditions.append(
            "tpr.department in ({})".format(
                ",".join(["'%s'" % d for d in filters.department if d in names])
            )
        )
    return conditions and " where " + " and ".join(conditions) or ""


def get_columns():

    return csv_to_columns(
        """
        Academic Year,academic_year,,,150
        Academic Term,academic_term,,,150
        Class,program,,,120
        Division,division,,120
        G R No,g_r_number,,,95
		ID No.,student,Link,Student,190
        Name,student_name,,,250
        Quarter,description,,,130
        Due Date,due_date,Date,,120
		Total Amount,grand_total,Currency,,130
		Paid Amount,paid_amount,Currency,,130
		Pending Amount,outstanding_amount,Currency,,130
    """
    )
    # Additional Amount,additional_amount,Currency,,130
    # Exemption Amount,exemption_amount,Currency,,130
    # NA Amount,na_amount,Currency,,130
