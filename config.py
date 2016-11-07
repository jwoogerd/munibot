# Number of minutes before the next train arrival that we aim
# to post an alert to Slack.
LOOKAHEAD_MINS = 9

# Days of week for which the Slackbot should be active. Monday is 0, Sunday is 6.
ACTIVE_WEEKDAYS = [0, 1, 2, 3, 4]

# The hour starting from which the Slackbot should be active.
START_HOUR = 17

# The hour at which the Slackbot should be inactive.
END_HOUR = 20
