"""Sims-style player notifications for the delivery coordinator."""


def show_delivery_notification(event):
    from sims4communitylib.notifications.common_basic_notification import CommonBasicNotification

    if event == "delivered":
        title = "Life Journal delivered!"
        message = "Your package is at the front door."
    elif event == "collected":
        title = "Life Journal collected"
        message = "Your Life Journal is in your inventory."
    else:
        raise ValueError("Unknown Life Journal notification: " + event)
    CommonBasicNotification(title, message).show()
