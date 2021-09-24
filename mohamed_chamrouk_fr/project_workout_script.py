# correspondance dict
import re
import json


exercise_dict = {
    "dev_couche_barre": ["dc", "dev couche barre", "dev couche"],
    "dev_couche_haltere": ["dev haltere"],
    "dev_arnold": ["dev arnold"],
    "dev_incline_haltere": ["devhalt", "dev incline"],
    "dev_incline_barre": ["di"],
    "ecarte_couche": ["ec"],
    "curl_ez_barre": ["cbez"],
    "curl_alterne": ["ca"],
    "curl_banc": ["curl banc"],
    "curl_spider": ["curl spider"],
    "squat_arriere": ["squat arriere"],
    "presse_inclinee": ["presse inclinee", "presse"],
    "presse_jambe": ["pr"],
    "leg_extension": ["le", "legex", "leg extension", "extension"],
    "leg_curl": ["lc"],
    "leg_curl_assis": ["leg curl"],
    "souleve_romain_haltere": ["souleve"],
    "dev_militaire_cadre_guide": ["dmcg"],
    "elevation_laterale": ["el", "elev laterale"],
    "oiseau_haltere": ["oi", "oiseau haltere", "oiseaux halteres", "oiseau haltere assis"],
    "haussements_epaules": ["haussements epaules"],
    "v_squat": ["v squat"],
    "tirage_devant": ["td", "tirage devant"],
    "tirage_nuque": ["tn"],
    "tirage_neutre": ["tirage serre", "tirage neutre"],
    "rowing_haltere": ["rowing haltere"],
    "rowing_assis": ["ra", "rowing assis"],
    "elevation_barre_front": ["ebf", "cbf", "barre front"],
    "extension_haltere_nuque": ["ehn", "extensions haltere"],
    "extension_poulie_haute": ["extension poulie haute"],
    "poulie_vis_a_vis": ["poulie vis à vis"],
    "shoulder_press": ["sp", "shoulder press"],
    "traction": ["pull up"]
}


open('templates/projects/workout/temp_workout_data_output.json', 'w').close()

def write_json(json_data, key, filename='templates/projects/workout/temp_workout_data_output.json'):
    with open(filename, 'r+') as wfile:
        json_session = json.load(wfile)
        json_session[key].append(json_data)
        wfile.seek(0)
        json.dump(json_session, wfile, indent=4)


with open('templates/projects/workout/temp_workout_data_extract') as file:
    Lines = file.readlines()
    session = '{"sessions":[]}'
    with open('templates/projects/workout/temp_workout_data_output.json', 'r+') as wfile:
        wfile.write(session)
    i = -1
    line_number = 0
    for line in Lines:
        line_number += 1
        line = line.lower()

        if line[:4] in ['push', 'pull', 'legs']:
            i += 1
            date = line[5:line.find(':')].replace(' ', '').replace(':', '').\
                replace('\n', '')+'/21'
            if line.find('(') != -1:
                global_notes = line[line.find('(')+1:line.find(')')]
            else:
                global_notes = ""
            json_data = {"date": date, "lifts": [], "global_notes": global_notes}
            write_json(json_data, 'sessions')
        elif line[0].isalpha():
            for k, v in exercise_dict.items():
                if line[:line.find(':')-1] in v:
                    exercise = k

            remaining = line[line.find(':')+1:].replace('\n','')+' '
            json_sets = []
            notes = []

            if remaining.find('(') != -1:
                parenthesis = re.findall(r'\((.*?)\)', remaining)
                for p in parenthesis:
                    if any(c.isalpha() for c in p):
                        notes += [p]
                        remaining = remaining.replace(f"({p})", '')
                    elif (p == '~'):
                        notes += [p]
                        remaining.replace(f"({p})", "")
                    else:
                        reps = remaining[remaining.find('(')+1:remaining.find(')')].split(' ')
                if remaining.find('~'):
                    notes += ['meh']
                    remaining = remaining.replace('~', '')

            dict_lift = {}
            for idx,r in enumerate(re.findall(r' (.*?)-', remaining)):
                if (r,[re.sub("[^0-9.]", "", x) for x in re.findall(r'-(.*?) ', remaining+' ')][idx]) in dict_lift.items():
                    print('non')
                    dict_lift[str(int(r)+1)] = [re.sub("[^0-9.]", "", x) for x in re.findall(r'-(.*?) ', remaining+' ')][idx]
                else:
                    dict_lift[r] = [re.sub("[^0-9.]", "", x) for x in re.findall(r'-(.*?) ', remaining+' ')][idx]
            
            for r, w in dict_lift.items():
                if r.find('(') != -1:
                    r = [int(x) for x in r.replace('(', '').replace(')', '').split(' ')]
                    json_sets += [{"weight": float(w), "reps": r}]
                elif r.find('x') != -1:
                    json_sets += [{"weight": float(w), "reps": [int(r[r.find('x')+1:]) for i in range(int(r[:r.find('x')]))]}]
                else:
                    json_sets += [{"weight": float(w), "reps": int(r)}]
            json_data = {"exercise": exercise, "sets": json_sets, "notes": notes}

            with open('templates/projects/workout/temp_workout_data_output.json', 'r+') as wfile:
                json_session = json.load(wfile)
                json_session["sessions"][i]["lifts"].append(json_data)
                wfile.seek(0)
                json.dump(json_session, wfile, indent=4)

"""def write_json(json_data, key, filename='templates/projects/workout/temp_workout_data_output.json'):
    with open(filename, 'r+') as wfile:
        json_session = json.load(wfile)
        json_session[key].append(json_data)
        wfile.seek(0)
        json.dump(json_session, wfile, indent=4)


with open('templates/projects/workout/temp_workout_data') as file:
    Lines = file.readlines()
    session = '{"sessions":[]}'
    with open('templates/projects/workout/temp_workout_data_output.json', 'r+') as wfile:
        wfile.write(session)
    i = -1
    for line in Lines:
        line = line.replace("•", "").replace(" ", "", 1).lower()
        line = re.sub("[\(\[].*?[\)\]]", "", line)

        if line.find('/') != -1:
            i += 1
            date = line.replace(' ', '').replace(':', '').replace('\n', '')+'/21'
            json_data = {"date": date, "lifts": []}
            write_json(json_data, 'sessions')

        if line.find('-') != -1 and line[line.find('-')-1].isalpha():

            newline = line[line.find('-')+1:]
            for k, v in exercise_dict.items():
                if line[:line.find('-')] in v:
                    exercise = k

            json_data = {"exercise": exercise, "sets": []}
            lift = {}
            weight = float(newline[:newline.find("kg")])
            remaining = newline[newline.find(":")+1:].replace('\n', '')

            if not any(c.isalpha() for c in remaining):  #TODO A transformer en boucle while
                reps = [float(x) for x in remaining.replace(' ', '').split('-')]
                json_sets = {"weight": weight, "reps": reps}
            else:
                reps = [float(x) for x in remaining[:remaining.find('kg')].rsplit(' ', 1)[0].replace(' ', '').split('-')]
                weight_bis = float(remaining[:remaining.find('kg')].rsplit(' ', 1)[1])
                reps_bis = [float(x) for x in remaining[remaining.find('kg')+2:].replace(' ', '').replace(':','').split('-')]
                json_sets = {"weight": weight, "reps": reps}, {"weight": weight_bis, "reps": reps_bis}

            json_data = {"exercise": exercise, "sets": [json_sets]}

            with open('templates/projects/workout/temp_workout_data_output.json', 'r+') as wfile:
                json_session = json.load(wfile)
                json_session["sessions"][i]["lifts"].append(json_data)
                wfile.seek(0)
                json.dump(json_session, wfile, indent=4)"""
