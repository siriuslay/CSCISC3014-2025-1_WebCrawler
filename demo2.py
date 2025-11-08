from demo.ticket_grabber import TicketGrabber


concert_url = "https://m.damai.cn/shows/item.html?itemId=989000117699"

grabber = TicketGrabber()
grabber.start_browser(headless=False)

success = grabber.grab_ticket(concert_url)
print(success)

import time
time.sleep(10)
grabber.close()

