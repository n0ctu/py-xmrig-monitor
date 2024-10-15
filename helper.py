# Helper functions for data formatting
def shorten_string(value, max_length):
    if len(value) > max_length:
        return value[:max_length - 3] + "..."
    return value

def seconds_to_string(seconds):
    years = seconds // 31536000
    months = (seconds % 31536000) // 2592000
    days = (seconds % 2592000) // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if years > 0:
        return f"{years} Years {months} Months {days} Days"
    elif months > 0:
        return f"{months} Months {days} Days {hours} Hours"
    elif days > 0:
        return f"{days} Days {hours} Hours {minutes} Minutes"
    elif hours > 0:
        return f"{hours} Hours {minutes} Minutes {seconds} Seconds"
    elif minutes > 0:
        return f"{minutes} Minutes {seconds} Seconds"
    else:
        return f"{seconds} Seconds"
    
