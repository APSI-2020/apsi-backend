# apsi-backend

## Requirements

### Membership requirment
If user want to participate in the event, he has to fullfil membership requirements (if they are specified by the host).  
That means that he has to be in specific user groups.

#### User Groups:
* Bachelor Students,
* Master Students,
* Doctoral Students,
* Guests,
* Lecturers
* Course specific (for example students that take APSI course, there can be many of those)


#### Possible schemas
* User belongs to any of specified groups and takes APSI or BEST course
```
[
  {
    "type": "BELONGS_TO_ANY_OF",
    "groups": ['Bachelor Students', 'Master Students', 'APSI']
  }
]
```
* User does not belong to any of those groups and does not take APSI and BEST courses
```
[
  {
    "type": "DOES_NOT_BELONG_TO_ANY_OF",
    "groups": ['Bachelor Students', 'Master Students']
  }
]
```
* User belongs to execatly those groups and take both APSI and BEST courses
```
[
  {
    "type": "BELONGS_EXACTLY_TO",
    "groups": ['Guests', 'Lecturers']
  }
]
```

## How to load mock data
Some mock data have been generated with [Mockaroo](https://www.mockaroo.com/)

There are two ways of loading mock data:
1. Run server (python3 manage.py runserver or via IDE)
2. Run script mock_data/generate_data.sh (bash mock_data/generate_data.sh)
or
1. Run migrations (python3 manage.py migrate)
2. Load data from .json file (python3 manage.py loaddata mock_data/dump.json)
