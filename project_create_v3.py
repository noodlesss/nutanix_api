import requests, json, argparse, sys
from pprint import pprint

# To create Porject:
# call script from command line with "--action project_create"
# Script will update config file with newly created project uuid
# To create access control policy:
# call script from command line with "--action acp_create"
# To associate project with user/user_group list: 
# call script from command line with "--action project_update"

## Required parameters in config file:
##  - subnets list
##  - project name
##  - access control policy role uuid. can be obtained with 'nuclei role.list' command from Prism Central
##  - access control  user_reference_list or user_group_reference_list. 'nuclei user.list' or 'nuclei user_group.list'
##  - urename
##  - password
##  - Prism Central ip


project_specs = {  
  "spec":{  
    "name":"nuran3",
    "resources":{  
      "subnet_reference_list":[  
        {  
          "kind":"subnet",
          "uuid":"e8d8eaab-0a43-496c-875c-e0a74df546b4"
        }
      ]
    },
    "description":"asd"
  },
  "metadata":{  
    "kind":"project"
  }
}

acp_specs = {  
  "spec":{  
    "name":"nuran_acp",
    "resources":{  
      "role_reference":{  
        "kind":"role",
        "uuid":"3d5f6fc8-42a8-4d3e-918c-d9944d2893e8"
      },
      "user_reference_list":[  
        {  
          "kind":"user",
          "uuid":"9badc8c8-ccda-5133-a2d0-019aa346db8a"
        }
      ],
      "filter_list":{  
        "context_list":[  
          {  
            "entity_filter_expression_list":[  
              {  
                "operator":"IN",
                "left_hand_side":{  
                  "entity_type":"ALL"
                },
                "right_hand_side":{  
                  "collection":"ALL"
                }
              }
            ],
            "scope_filter_expression_list":[  
              {  
                "operator":"IN",
                "right_hand_side":{  
                  "uuid_list":[  
                    ""
                  ]
                },
                "left_hand_side":"PROJECT"
              }
            ]
          }
        ]
      },
      "user_group_reference_list":[  
        {  
          "kind":"user_group",
          "uuid":""
        }
      ]
    },
    "description":"Description of ACP"
  },
  "metadata":{  
    "kind":"access_control_policy"
  }
}

project_update = {  
  "spec":{  
    "name":"",
    "resources":{  
      "resource_domain":{  
        "resources":[  

        ]
      },
      "user_reference_list":[  
        {  
          "kind":"user",
          "uuid":"bc062a02-a5cb-5c04-9084-c8d4b627dc46"
        }
      ],
      "external_user_group_reference_list":[  
        {  
          "kind":"user_group",
          "uuid":"bc062a02-a5cb-5c04-9084-c8d4b627dc46"
        }
      ],
      "subnet_reference_list":[  
        {  
          "kind":"subnet",
          "uuid":"923ac8ef-d867-401b-b354-9043901c41bb"
        },
        {  
          "kind":"subnet",
          "uuid":"24da64b2-b6af-4493-9ab7-340cb8bb627c"
        }
      ]
    }
  },
  "metadata":{  
    "owner_reference":{  
      "kind":"user",
      "uuid":"00000000-0000-0000-0000-000000000000",
      "name":"admin"
    },
    "kind":"project",
    "spec_version":0,
    "uuid":""
  }
}


user_query_specs = {
  "query": "<group_name_to_be_searched>",
  "returned_attribute_list": ["memberOf", "member", "userPrincipalName", "distinguishedName"],
  "searched_attribute_list": ["name", "userPrincipalName", "distinguishedName"]
}

user_create_specs = {
    "spec": {
        "resources": {
            "directory_service_user_group": {
                "distinguished_name": "<distinguished_name_from_step_2>"
            }
        }
    }, 
    "metadata": {
        "kind": "user_group"
    }
}


class nutanixApi(object):
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password

    def project_create(self, body):
        requests.packages.urllib3.disable_warnings()
        s = requests.Session()
        s.auth = (self.username, self.password)
        s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        data = s.post(self.base_url + 'projects', json=body, verify=False)
        return data   

    def create_acp(self, body):
        requests.packages.urllib3.disable_warnings()
        s = requests.Session()
        s.auth = (self.username, self.password)
        s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        data = s.post(self.base_url + 'access_control_policies', json=body, verify=False)
        return data

    def project_update(self, project_uuid, body):
        requests.packages.urllib3.disable_warnings()
        s = requests.Session()
        s.auth = (self.username, self.password)
        s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        data = s.put(self.base_url + 'projects/%s' %project_uuid, json=body, verify=False)
        return data
    
    def user_query(self, directory_service_uuid, body):
        requests.packages.urllib3.disable_warnings()
        s = requests.Session()
        s.auth = (self.username, self.password)
        s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        data = s.post(self.base_url + 'directory_services/%s/search' %directory_service_uuid, json=body, verify=False)
        return data


def body_generator(bodyname, project_data):
    if bodyname == 'project_create':
        project_specs['spec']['name'] = project_data['project']['project_name']
        project_specs['spec']['description'] = project_data['project']['project_description']
        subnets = project_data['project']['subnets']
        subnets_list = []
        for i in subnets:
            subnets_list.append({'kind': 'subnet', 'uuid': i})
        project_specs['spec']['resources']['subnet_reference_list'] = subnets_list
        return project_specs
    elif bodyname == 'acp_create':
        acp_specs['spec']['name'] = project_data['acp']['acp_name']
        acp_specs['spec']['description'] = project_data['acp']['acp_description']
        user_group_reference_list = project_data['acp']['acp_user_group_reference_list']
        ugrl_list = []
        for i in user_group_reference_list:
            ugrl_list.append({'kind': 'user_group', 'uuid': i})
        acp_specs['spec']['resources']['user_group_reference_list'] = ugrl_list
        user_reference_list = project_data['acp']['acp_user_reference_list']
        url_list = []
        for i in user_reference_list:
            url_list.append({'kind': 'user', 'uuid': i})
        acp_specs['spec']['resources']['user_reference_list'] = url_list
        acp_specs['spec']['resources']['role_reference']['uuid'] = project_data['acp']['acp_role']
        acp_specs['spec']['resources']['filter_list']['context_list'][0]['scope_filter_expression_list'][0]['right_hand_side']['uuid_list'][0] = project_data['project_update']['uuid']
        return acp_specs
    elif bodyname == 'project_update':
        project_update['metadata']['uuid'] = project_data['project_update']['uuid']
        project_update['metadata']['spec_version'] = project_data['project_update']['spec_version']
        project_update['spec']['name'] = project_data['project']['project_name']
        user_group_reference_list = project_data['acp']['acp_user_group_reference_list']
        ugrl_list = []
        for i in user_group_reference_list:
            ugrl_list.append({'kind': 'user_group', 'uuid': i})
        project_update['spec']['resources']['external_user_group_reference_list'] = ugrl_list
        user_reference_list = project_data['acp']['acp_user_reference_list']
        url_list = []
        for i in user_reference_list:
            url_list.append({'kind': 'user', 'uuid': i})
        project_update['spec']['resources']['user_reference_list'] = url_list
        subnets = project_data['project']['subnets']
        subnets_list = []
        for i in subnets:
            subnets_list.append({'kind': 'subnet', 'uuid': i})
        project_update['spec']['resources']['subnet_reference_list'] = subnets_list
        return project_update
    elif bodyname == 'user_query':
        user_query_specs['query'] = project_data['user']['user_name']
        return user_query_specs




def main():
    parser = argparse.ArgumentParser(description='creating project via Nutanix v3 API')
    parser.add_argument('--action', action='store', dest='command', help='action can be: project_create, acp_create, project_update')
    results = parser.parse_args()
    command = results.command
    try:
        with open('project_data.json') as fl: project_data = json.load(fl)
    except Exception as e:
        print (e)
        sys.exit(1)
    general_info = project_data['general']
    username = general_info['username']
    password = general_info['password']
    cluster_ip = general_info['pc_ip']
    body = body_generator(command, project_data)
    base_url = "https://%s:9440/api/nutanix/v3/" %cluster_ip
    project = nutanixApi(base_url, username, password)
    if command == 'project_create':
        data = project.project_create(body)
        try:
            data = data.json()
        except Exception as e:
            print ('error: %s' %e)
        print (data)
        if data['metadata']['kind'] == 'project':
            project_uuid = data['metadata']['uuid']
            project_spec_version = data['metadata']['spec_version']
            project_data['project_update']['uuid'] = project_uuid
            project_data['project_update']['spec_version'] = project_spec_version
            project_data['acp']['acp_project_uuid'] = project_uuid
            with open('project_data.json', 'w') as fl: json.dump(project_data, fl)
        else:
            print ('response metadata is not "project"')
            sys.exit(1)
    elif command == 'project_update':
        data = project.project_update(project_data['project_update']['uuid'], body)
        try:
            data = data.json()
        except Exception as e:
            print ('error: %s' %e)
        print (data)
    elif command == 'acp_create':
        data = project.create_acp(body)
        try:
            data = data.json()
        except Exception as e:
            print ('error: %s' %e)
        print (data)
    elif command == 'user_query':
      directory_service_uuid = project_data['user']['directory_service_uuid']
      data = project.user_query(directory_service_uuid, body)
      try:
          data = data.json()
      except Exception as e:
          print ('error: %s' %e)
      pprint(data)
    else:
        print ('wrong command, try one of this: project_create, project_update, acp_create')
        sys.exit(1)



if __name__ == '__main__':
    main()

