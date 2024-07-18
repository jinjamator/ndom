

def i_dont_care():
    printer=BaseRenderer()

    jsonwriter=JSONRenderer()
    yamlwriter=YAMLRenderer()

    switch3.add_render_plugin(jsonwriter)
    switch3.add_render_plugin(yamlwriter)
    # switch3.add_render_plugin(printer)

    from pprint import pprint
    data=switch3.render(json_path="switch.json",yaml_path="switch.yaml",overwrite=True)

    parsed_data=json.loads(data[0][1])
    pprint(parsed_data)
    test_loader=BaseLoader()
    print("result")
    print(test_loader.load(data=parsed_data))