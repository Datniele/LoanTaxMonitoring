import numpy as np
import pandas as pd
from dateutil import relativedelta


def tax_var_analysis(dtf_tax):
    dtf_tax["AM"] = dtf_tax["Date"].dt.strftime('%Y%m')
    dtf_gb_am = dtf_tax.groupby("AM").agg(TAX_MEAN=("Tasso", np.mean),
                                          N_CASI=("Date", "count")).reset_index()

    dtf_gb_am = dtf_gb_am[-2:].copy()
    dtf_gb_am.sort_values("AM", inplace=True)
    if len(dtf_gb_am) < 2:
        return None
    ser_last_months = pd.to_datetime(dtf_gb_am["AM"][-2:] + "01")
    int_diff_months_last_two_rows = relativedelta.relativedelta(ser_last_months[1], ser_last_months[0]).months
    if int_diff_months_last_two_rows == 1 and dtf_gb_am["N_CASI"].min() >= 15:
        flt_tax_diff = (dtf_gb_am["TAX_MEAN"] / dtf_gb_am["TAX_MEAN"].shift(1)).tail(1).values[0]
        if flt_tax_diff - 1 <= -0.1:
            return {"tax_delta": flt_tax_diff - 1, "summary": dtf_gb_am}

    return None
