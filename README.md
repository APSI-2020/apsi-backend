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
* User belongs to any of:
[
  {
    "type": "BELONGS_TO_ANY_OF",
    "groups": ['Bachelor Students', 'Master Students']
  },
  {
    "type": "TAKES_ANY_OF",
    "courses": ['APSI']
  }
]

* User does not belong to any of
[
  {
    "type": "DOES_NOT_BELONG_TO_ANY_OF",
    "groups": ['Bachelor Students', 'Master Students']
  },
  {
    "type": "DOES_NOT_TAKE_ANY_OF",
    "groups": ['APSI', 'BEST']
  }
]

* User belongs to execatly those groups:
[
  {
    "type": "BELONGS_EXACTLY_TO",
    "groups": ['Guests', 'Lecturers']
  },
  {
    "type": "TAKES_EXACTLY_THOSE",
    "groups": ['APSI', 'BEST']
  }
]
