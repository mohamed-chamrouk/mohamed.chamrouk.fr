import mohamed_chamrouk_fr
import requests
import json
from mohamed_chamrouk_fr import app
import mohamed_chamrouk_fr.startup as startup
from flask import (redirect, Blueprint, request, render_template, url_for,
                   make_response)
from flask_login import login_required

wkt = Blueprint('project_workout', __name__)


img_dict = {
    "dev_couche_barre": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Barbell-Bench-Press_0316b783-43b2-44f8-8a2b-b177a2cfcbfc_600x600.png",
    "dev_couche_haltere": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Dumbbell-Bench-Press_13090f67-ccfc-4f3a-9bab-e75d753fa9fa_600x600.png?v=1612137970",
    "dev_arnold": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Dumbbell-Shoulder-Press_da0aa742-620a-45f7-9277-78137d38ff28_600x600.png?v=1612138495",
    "dev_incline_haltere": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Incline-Dumbbell-Bench-Press_c2bf89a2-433f-4a8f-9801-67c679980867_600x600.png?v=1612138008",
    "dev_incline_barre": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Incline-Barbell-Bench-Press_dc0c6279-d038-44f5-a682-54c2a5e2602c_600x600.png?v=1612137944",
    "ecarte_couche": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Dumbbell-Fly_119e2918-4241-4f55-bd77-c98a0c76c6c8_600x600.png?v=1612137840",
    "curl_ez_barre": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/EZ-Barbell-Curl_42cb566b-6415-4318-94e0-c93f4b442e59_600x600.png?v=1612137227",
    "curl_alterne": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Alternating-Dumbbell-Curl_ad879dc4-b4fb-4ca7-b2b1-6e1eb5d78252_600x600.png?v=1612137169",
    "curl_banc": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Incline-Dumbbell-Curl_7debf468-cd34-49bc-8933-7f4b087e6cca_600x600.png?v=1612137309",
    "curl_spider": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/EZ-Barbell-Preacher-Curl_4d449fee-1920-4137-970c-75d4698b268d_600x600.png?v=1612137254",
    "squat_arriere": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Squat_d752e42d-02ba-4692-b300-c6e67ad5a4f5_600x600.png?v=1612138811",
    "presse_inclinee": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Leg-Press_f7febd5c-75e5-42f4-9bb4-c938969ce293_600x600.png?v=1612138836",
    "presse_jambe": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Leg-Press_f7febd5c-75e5-42f4-9bb4-c938969ce293_600x600.png?v=1612138836",
    "leg_extension": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Leg-Extension_41d91d3f-4b9c-4374-82e2-1d697ce35fe4_600x600.png?v=1612138862",
    "leg_curl": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Lying-Leg-Curl_203153d8-79dd-4bb9-9125-708aa4327107_600x600.png?v=1612139013",
    "leg_curl_assis": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Seated-Leg-Curl_e367789a-bbb3-4144-a926-5a9b42afc278_600x600.png?v=1612139123",
    "souleve_romain_haltere": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Dumbbell-Romanian-Deadlift_35135213-e0df-4ef2-b093-22ed8d04dc41_600x600.png?v=1621162896",
    "dev_militaire_cadre_guide": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Smith-Machine-Shoulder-Press_e53bea60-c273-41e9-a70d-f5fa339c6780_600x600.png?v=1612138658",
    "elevation_laterale": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Dumbbell-Lateral-Raise_31c81eee-81c4-4ffe-890d-ee13dd5bbf20_600x600.png?v=1612138523",
    "oiseau_haltere": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Bent-Over-Lateral-Raise_41bd4de4-0370-4e6b-9501-37cdcc26ded4_600x600.png?v=1621163232",
    "haussements_epaules": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Dumbbell-Shrugs_69a32385-3573-471b-a66e-3abdb0d95819_600x600.png?v=1619986777",
    "v_squat": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Hack-Squat_044b3d09-ffa7-4728-b56f-f4fb3c175548_600x600.png?v=1612139060",
    "tirage_devant": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Wide-Grip-Pulldown_91fcba9b-47a2-4185-b093-aa542c81c55c_600x600.png?v=1612138105",
    "tirage_nuque": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Behind-Neck-Pulldown_f0f50b6b-ad34-48cd-8663-84ee6a581928_600x600.png?v=1612138228",
    "tirage_neutre": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Close-Grip-Pulldown_072bb5ce-e3d9-4007-b8d2-d343e9d1051b_600x600.png?v=1612138178",
    "rowing_haltere": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Dumbbell-Bent-Over-Rows_600x600.png?v=1619977463",
    "rowing_assis": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Seated-Cable-Row_9470fa48-f0d1-40b1-a980-caee9e6f2e53_600x600.png?v=1612138127",
    "elevation_barre_front": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Lying-Triceps-Extension_4affa7a2-9c1c-48f8-8003-3570d7b3a39c_600x600.png?v=1612136744",
    "extension_haltere_nuque": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Dumbbell-Overhead-Triceps-Extension_99242f13-ab4d-4e77-be12-e0f180cc93ac_600x600.png?v=1612136962",
    "extension_poulie_haute": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Cable-Rope-Pushdown_600x600.png?v=1612136916",
    "poulie_vis_a_vis": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Cable-Crossover_09c90616-2777-47ed-927e-d5987edfce09_600x600.png?v=1612138036",
    "shoulder_press": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Barbell-Push-Press_8ba0542a-aba8-45ce-bdee-1a3eb4736514_600x600.png?v=1621162658",
    "traction": "https://cdn.shopify.com/s/files/1/0269/5551/3900/files/Pull-Up_600x600.png?v=1619977612"
}

@wkt.route("/projects/workout/")
@login_required
def workout():
    with open('mohamed_chamrouk_fr/templates/projects/workout/temp_workout_data_output.json') as jsonFile:
        jsonWorkout = json.load(jsonFile)
        jsonFile.close()

    sessions = jsonWorkout['sessions']
    return render_template('projects/workout/workout_home.html', sessions=sessions, exercises=list(img_dict.keys()))

@wkt.route("/projects/workout/<string:date>/")
@login_required
def workout_detail(date):
    date=date.replace('-', '/')
    with open('mohamed_chamrouk_fr/templates/projects/workout/temp_workout_data_output.json') as jsonFile:
        jsonWorkout = json.load(jsonFile)
        jsonFile.close()
    session = []
    for workout in jsonWorkout['sessions']:
        if workout['date'] == date:
            session += [workout]
    app.logger.info(f"{session} et {session[0]}")
    return render_template('projects/workout/workout_single.html', workout=session[0], img_dict=img_dict, type=type)

@wkt.route('/projects/workout/edit_json/', methods=('GET', 'POST'))
@login_required
def workout_edit_json():
    with open('mohamed_chamrouk_fr/templates/projects/workout/temp_workout_data_output.json') as jsonFile:
        jsonWorkout = json.load(jsonFile)
        jsonFile.close()

    if request.method == 'POST':
        new_json = request.form['json']
        open('mohamed_chamrouk_fr/templates/projects/workout/temp_workout_data_output.json', 'w').close()
        with open('mohamed_chamrouk_fr/templates/projects/workout/temp_workout_data_output.json', 'r+') as jsonFile:
            jsonFile.seek(0)
            json.dump(new_json, jsonFile, indent=4)
        return redirect(url_for('project_workout.workout'))

    return render_template('projects/workout/workout_edit_json.html', jsonFile=jsonWorkout)

"""@wkt.route('/projects/workout/add/', methods=('GET', 'POST'))
@login_required
def workout_add():
    with open('mohamed_chamrouk_fr/templates/projects/workout/temp_workout_data_output.json') as jsonFile:
        jsonWorkout = json.load(jsonFile)
        jsonFile.close()

    if request.method == 'POST':
        new_json = request.form['json']
        open('mohamed_chamrouk_fr/templates/projects/workout/temp_workout_data_output.json', 'w').close()
        with open('mohamed_chamrouk_fr/templates/projects/workout/temp_workout_data_output.json', 'r+') as jsonFile:
            jsonFile.seek(0)
            json.dump(new_json, jsonFile, indent=4)
        return redirect(url_for('project_workout.workout'))

    return render_template('projects/workout/workout_edit_json.html', jsonFile=jsonWorkout)"""

@wkt.route('/projects/workout/lift/<string:lift>/')
@login_required
def workout_add(lift):
    with open('mohamed_chamrouk_fr/templates/projects/workout/temp_workout_data_output.json') as jsonFile:
        jsonWorkout = json.load(jsonFile)['sessions']
        jsonFile.close()

    stat_dict = {}

    for session in jsonWorkout:
        for exercise in session['lifts']:
            if exercise['exercise'] == lift:
                stat_dict[session['date']] = max([set['weight'] for set in exercise['sets']])
                
    return render_template('projects/workout/workout_graph.html', xValues=list(stat_dict.keys()), yValues=list(stat_dict.values()))