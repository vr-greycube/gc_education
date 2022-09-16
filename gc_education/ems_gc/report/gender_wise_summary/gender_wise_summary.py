# Copyright (c) 2022, Greycube and contributors
# For license information, please see license.txt

import frappe
from gc_education.ems_gc.report import csv_to_columns
import pandas
import numpy as np


def execute(filters=None):
    return get_data(filters)


def get_data(filters):
    data = frappe.db.sql(
        """
    select 
        ts.name , ts.religion , ts.gender , tpe.program class, tpe.student_batch_name division ,
         tpe.academic_year , tpe.academic_term
    from tabStudent ts 
    inner join `tabProgram Enrollment` tpe on tpe.student = ts.name 	
    inner join `tabProgram` tpr on tpr.name = tpe.program
    {cond}
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
            "class",
            "division",
        ],
        values=["name"],
        columns=["gender"],
        fill_value=0,
        margins=True,
        margins_name="Total",
        aggfunc="count",
        dropna=True,
    )
    df1.drop(index="Total", axis=0)
    df1.columns = df1.columns.to_series().str[1]
    df2 = df1.reset_index()

    columns = get_columns()

    for col in df1.columns.to_list():
        columns += [
            dict(label=col, fieldname=col, fieldtype="Int", width=140),
        ]

    columns[-1]["label"] = "Total"

    out = []
    for d in df2.to_dict("r"):
        out.append({k: v for k, v in d.items() if v})
    out[-1]["bold"] = 1

    return columns, out


def get_conditions(filters):
    conditions = []
    if filters.get("academic_year"):
        conditions.append(" tpe.academic_year = %(academic_year)s")
    if filters.get("academic_term"):
        conditions.append(" tpe.academic_term = %(academic_term)s")
    if filters.get("batch"):
        lst = filters.batch
        # to prevent SQL Injection
        batches = frappe.get_list("Student Batch Name", pluck="name")
        conditions.append(
            "tpe.student_batch_name in ({})".format(
                ",".join(["'%s'" % d for d in lst if d in batches])
            )
        )
    if filters.get("student_status") and not filters.student_status == "All":
        conditions.append(
            "ts.enabled = {}".format(
                filters.get("student_status") == "Enabled" and 1 or 0
            )
        )
    if filters.get("program"):
        lst = filters.program
        # to prevent SQL Injection
        programs = frappe.get_list("Program", pluck="name")
        conditions.append(
            "tpe.program in ({})".format(
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
    Academic Year,academic_year,,,160
    Academic Term,academic_term,,,160
    Class,class,,,145
    Division,division,,,145
    """
    )
