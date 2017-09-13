from __future__ import print_function
import json, urllib
from decimal import Decimal


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_speechlet_response2(title, output, output2, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml':  "<speak>" + output2 + "</speak>"
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    
    # response = urllib.urlopen('https://world.openfoodfacts.org/api/v0/product/737628064502.json')
    # output = json.loads(response.read())

    # name = output['product']['product_name']
    
    name = 'Welcome to Food Facts, please specify a barcode one number at a time'

    
    speech_output = name
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please specify a barcode one number at a time"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using Food Facts"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = 'Setting Barcode'
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        favorite_color = favorite_color.replace(" ", "")
        favorite_color = favorite_color.replace('mybarcodeis','')
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your barcode "  + \
                        favorite_color + \
                        ". You can ask me your food facts by saying, " \
                        "what are my macros?"
        speech_output2 = "I now know your barcode "  + \
                        '<say-as interpret-as="digits">' + favorite_color + "</say-as>" + \
                        ". You can ask me your food facts by saying, " \
                        "what are my macros?"
        reprompt_text = "You can ask me your food facts by saying, " \
                        "what are the nutrition facts?"
        return build_response(session_attributes, build_speechlet_response2(
            card_title, speech_output, speech_output2, reprompt_text, should_end_session))
    else:
        speech_output = "I'm not sure what your barcode is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your barcode is. " \
                        "You can tell me your barcode by saying, " \
                        "my barcode is 00000000."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None
    
    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        favorite_color = favorite_color.replace(" ", "")
        favorite_color = favorite_color.replace('mybarcodeis','')
        url = "http://world.openfoodfacts.org/api/v0/product/" + str(favorite_color) + ".json"
        response = urllib.urlopen(url)
        output = json.loads(response.read())
        favorite_color = str(favorite_color)
        length = len(favorite_color)
            
        if output['status_verbose'] == "product found" and output['product']['nutriments']:
            name = output['product']['product_name']
            carbs = output['product']['nutriments']['carbohydrates']
            fat = output['product']['nutriments']['fat']
            protein = output['product']['nutriments']['proteins']
            speech_output = name + ", fat is " + str(fat) + " grams. carbs is " + str(carbs) + " grams. protein is " + str(protein) + " grams."
            should_end_session = True
        elif output['status_verbose'] == "product found":
            name = output['product']['product_name']
            speech_output = name + ", does not have nutrition facts listed in the openfoodfacts database"
            should_end_session = True
        else:
            speech_output = "I'm sorry that product is not found on openfoodfacts.org."
            should_end_session = True            
    else:
        speech_output = "I'm not sure what your barcode is. " \
                        "You can say, my barcode is 00000000."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        "Product Information", speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "MyColorIsIntent":
        return set_color_in_session(intent, session)
    elif intent_name == "WhatsMyColorIntent":
        return get_color_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

