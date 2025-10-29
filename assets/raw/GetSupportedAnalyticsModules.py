{
    'AnalyticsModuleContentSchemaLocation': [
        'http://www.w3.org/2001/XMLSchema'
    ],
    'AnalyticsModuleDescription': [
        {
            'Parameters': {
                'SimpleItemDescription': [
                    {
                        'Name': 'Sensitivity',
                        'Type': 'xs:integer'
                    }
                ],
                'ElementItemDescription': [
                    {
                        'Name': 'Layout',
                        'Type': 'tt:CellLayout'
                    }
                ],
                'Extension': None,
                '_attr_1': None
            },
            'Messages': [
                {
                    'Source': {
                        'SimpleItemDescription': [
                            {
                                'Name': 'VideoSourceConfigurationToken',
                                'Type': 'tt:ReferenceToken'
                            },
                            {
                                'Name': 'VideoAnalyticsConfigurationToken',
                                'Type': 'tt:ReferenceToken'
                            },
                            {
                                'Name': 'Rule',
                                'Type': 'xs:string'
                            }
                        ],
                        'ElementItemDescription': [],
                        'Extension': None,
                        '_attr_1': None
                    },
                    'Key': None,
                    'Data': {
                        'SimpleItemDescription': [
                            {
                                'Name': 'IsMotion',
                                'Type': 'xs:boolean'
                            }
                        ],
                        'ElementItemDescription': [],
                        'Extension': None,
                        '_attr_1': None
                    },
                    'Extension': None,
                    'ParentTopic': 'tns1:RuleEngine/CellMotionDetector/Motion',
                    'IsProperty': True,
                    '_attr_1': {
                }
                }
            ],
            'Extension': None,
            'Name': 'tt:CellMotionEngine',
            'fixed': True,
            'maxInstances': 1,
            '_attr_1': {
        }
        }
    ],
    'Extension': None,
    'Limit': None,
    '_attr_1': None
}