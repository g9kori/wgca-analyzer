import re
import pandas as pd

def preprocess(data):
    # Define patterns for both 12-hour and 24-hour formats
    pattern_12hr = r"\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:AM|PM)\s-\s"
    pattern_24hr = r"\d{1,2}/\d{1,2}/\d{2,4},\s\d{2}:\d{2}\s-\s"

    # First, check if data matches 12-hour or 24-hour format
    if re.search(pattern_12hr, data):
        pattern = pattern_12hr
        date_format = '%d/%m/%Y, %I:%M %p - '
    elif re.search(pattern_24hr, data):
        pattern = pattern_24hr
        date_format = '%d/%m/%Y, %H:%M - '
    else:
        raise ValueError("Date format not recognized. Please use either 12-hour or 24-hour format.")

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Convert message_date to datetime using the determined format
    df['message_date'] = pd.to_datetime(df['message_date'], format=date_format, errors='coerce')
    df.rename(columns={'message_date': 'date'}, inplace=True)

    # Separate users and messages
    users = []
    messages = []

    for message in df['user_message']:
        # Updated regex pattern to avoid invalid escape sequences
        entry = re.split(r'([^:]+):\s', message, maxsplit=1)
        if len(entry) > 2:  # Valid user-message format
            users.append(entry[1].strip())  # Extract user
            messages.append(entry[2].strip())  # Extract message
        else:
            users.append('group_notification')
            messages.append(entry[0])

    # Add extracted users and messages back to the DataFrame
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract date components
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create 'period' column for hour ranges
    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period
    return df