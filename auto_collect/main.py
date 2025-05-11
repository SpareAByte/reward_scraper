"""This is the main 'handler' of the app. This is what makes it scalable to test, login, explore etc."""

import json
import importlib

#Load handlers.
with open ('job_handler.json', 'r') as f:
    job_handler = json.load(f)

#Iterate through key/value to bring up the handler or function.
for site_name, job_config in job_handler.items():
    handler_path = job_config.get('handler')

    #You should not see this unless you have a typo.
    if not handler_path:
        print(f"No handler found for {site_name}.")
        continue
    
    try:
        #Splits the key/value into useable parts.
        module_path, class_name = handler_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        HandlerClass = getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        print(f"Error importing handler for {site_name}: {e}")
        continue
    
    print(f"\n--- Running handler for {site_name} ---")
    try:
        #Runs your site based from json.
        handler = HandlerClass()
        handler.run()
    except Exception as e:
        print(f"Handler for {site_name} failed: {e}")
