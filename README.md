tabulator
=========
A very temporary explanation, really need to update this:

It runs on a raspberry pi. We attach an rfid reader/writer and also used a USB
connected barcode scanner. Then we built a Curses application that would allow
you to either "login" with an rfid card or a barcode. We made a database that it
would check the login against and based on that it would allow you to start
scanning items to purchase.

When scanning items it would use some tricks to search the web for the barcode
and figure out what the item is without anyone ever having to enter it. It
queries a crowd-sourced database first and foremost to see if someone has
created an entry for the item containing a description of it. if that doesn't
work, it will do a google search and process the first 3-5 results to make a
guess at what the item is. 

In this manner it will let you add items to your cart by scanning them until you
want to check out. When you want to check out it will add it to your tab which
is also stored in the database. There are quite a few other interesting
features...
