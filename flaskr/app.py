from flask import Flask, request, render_template
import cycle_time
import lead_time_for_change
import call_commit_id
import deployment_freq

app = Flask(__name__, template_folder='template')


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/cycle_time", methods=["POST"])
def get_details():
    project_key = request.form["project_key"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]
    res_cycle = cycle_time.cycle_time(project_key, start_date, end_date)
    res_lead = lead_time_for_change.cycle_time_lead(project_key, start_date, end_date)
    res_mean = call_commit_id.cycle_time_failover(project_key, start_date, end_date)
    res_deploy = deployment_freq.deployment_freq(project_key, start_date, end_date)
    print(f"{res_cycle}\n {res_lead}\n {res_mean}\n {res_deploy}")
    return render_template("result.html")  # cycle_time=res_cycle, mean_time=res_mean, lead_time=res_lead
