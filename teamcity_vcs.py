import os
import json
import xmltodict
import requests
from dotenv import load_dotenv

load_dotenv()

def get_headers(token=os.getenv('token-value',"None")):

    headers = {
        'Authorization': 'Bearer {}'.format(token),
    }
    return headers

def get_projectinfo(url="https://teamcity.com",suburl="/app/rest/projects/id:_Root"):
    print("\n-----------API_Called------------\n")
    print(url+suburl)
    
    try:
        response = requests.get(url+suburl, headers=get_headers(),verify=False)
        response.raise_for_status()
        return json.dumps(xmltodict.parse(response.content), indent=2)
    except requests.exceptions.HTTPError as err :
        return err


if __name__== '__main__':

    teamcity_url = os.getenv('server-url',"https://teamcity.com") #teamcity endpoint

    project_data = json.loads(get_projectinfo(url=teamcity_url,suburl = "/app/rest/vcs-roots?locator=type:jetbrains.git,count:1000"))

    # nextsuburl = project_data["vcs-roots"]["@nextHref"]
    count = 0

    for vcsroot in project_data["vcs-roots"]["vcs-root"]:

        vcs_filterjson = {
            "vcs_id":"",
            "vcs_type":"",
            "project_id":"",
            "project_WebUrl":""
        }

        suburl = vcsroot["@href"]
        vcsroot_data = get_projectinfo(url = teamcity_url,suburl=suburl)

        if "404" in str(vcsroot_data):
            continue
        vcsroot_data = json.loads(vcsroot_data)["vcs-root"]

        vcs_filterjson["vcs_id"] = vcsroot_data["@id"]
        vcs_filterjson["vcs_type"] = vcsroot_data["@vcsName"]
        vcs_filterjson["project_id"] = vcsroot_data["project"]["@id"]
        vcs_filterjson["project_WebUrl"] = vcsroot_data["project"]["@webUrl"]

        with open("projectVCS.json", "r+") as json_file:
            file_data = json.load(json_file)
            file_data.append(vcs_filterjson)
            json_file.seek(0)
            json.dump(file_data,json_file,indent=2, default=str)
        
        count= count + 1
        print("\n--------------- DONE FOR {} projects -------------\n".format(count))