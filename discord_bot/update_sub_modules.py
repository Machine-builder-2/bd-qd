

modules = [
    {
        "name": "JSON Templating",
        "description": (
            'This module allows for you to reference base',
            'json files, which in turn speeds up development drastically,',
            'since you\'ll no longer need to program the basics'),
        "long_description": '''\
            <p>
                This allows you to create "base" or "template" files,
                which you can reference freely from other files in your
                behavior pack to build from. This, in turn, gives you the
                freedom to write far fewer lines of code for each item,
                block, entity or any other json files you write.
            </p>
        ''',
        "price": 0.8,
        "toggled": False,
        "uid": "ahwo"
    },
    {
        "name": "Item & Block Templates",
        "description": (
            'This module adds prebuilt item & block templates,',
            'simplifying the process of creating a bunch of different',
            'types of items, and a variety of blocks'),
        "long_description": '''\
            <p>
                This module is basically JSON templating, on steriods, for items & blocks.
                The main idea of this module is that it can be used to simplify
                the process of creating custom items & blocks greatly. There are
                now new simple structures that you can use to generate
                fully-functional item & block files from.
            </p>
        ''',
        "price": 1.2,
        "toggled": False,
        "uid": "akfn"
    },
    {
        "name": "FRG Tools",
        "description": (
            'This module provides quick access to premade code samples,',
            'which you can reference easily within your own files'),
        "long_description": '''\
            <p>
                Behold, the beautiful FRG, now stripped down to its most basic form.
                This module provides quick access to a lot of different structure
                generation templates, which greatly reduces the effort you need
                to put in to making randomly generating structures in your
                behavior packs.
            </p>
        ''',
        "price": 3,
        "toggled": False,
        "uid": "vowb"
    },
    {
        "name": "NPC Builder",
        "description": (
            'This module proves a tool for quick development',
            'of NPCS & other state-based entities,',
            'perfect for adventure maps & mini-games'),
        "long_description": '''\
            <p>
                This is the one, all powerful. This module allows you to create
                state-based sequences for entities, which is perfect for creating
                NPCs for a story game, or even just basic custom entities. The system
                is versatile and easy to get started with.
            </p>
        ''',
        "price": 4,
        "toggled": False,
        "uid": "pwny"
    }
]

if __name__ == '__main__':
    import json, copy

    js_json = copy.deepcopy(modules)
    for i,m in enumerate(js_json):
        m['description'] = f'js-modules-desc-{i}'
    json_str = json.dumps(js_json,indent=4)
    js_json_str = 'var buying_options = ' + json_str

    for i,m in enumerate(js_json):
        desc = modules[i]['description']
        desc_multiline = '\n'.join(desc)
        js_json_str = js_json_str.replace(
            f'\"js-modules-desc-{i}\"',
            '`'+desc_multiline+'`'
        )
    
    open('../html/sub_modules.js', 'w').write(js_json_str)