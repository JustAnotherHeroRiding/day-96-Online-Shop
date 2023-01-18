#Using what you have learnt by building the blog website using 
# Flask, you're now going to build your own eCommerce website. 
# Your website needs to have a working cart and checkout.
#It should be able to display items for sale and take real
# payment from users.
#It should have login/registration authentication features.
#Here is an example website:
#https://store.waitbutwhy.com/
#You should consider using the Stripe API:
#https://stripe.com/docs/payments/checkout

#Lets do a rework of the artist.mk website
#To do
#Create the db for users and items in the cart done
#create the forms for register and sign up done 
#Create pop up sign up and log in windows done
#Let's add a third table for items done
#It should have a name,price,img url,description,category,subcategory done

#items in the cart will have an id linking back to original item done
#second html page that will display the info for the clicked item done


#need to find a nice component to display the items using the data from the sql table done
#added checkout screen

#Lets make the add to cart button work now DONE
#Allow adding items to cart DONE
#save cart items to every user so they can come back and see them later DONE
#save them to a items table with the owner id check DONE

#Allow making payments DONE

#Next steps
#Remove item from cart when payment is succesful DONE

#Implement webhooks for payment confirmation DONE

#Fix static tax and shipping costs to per product DONE

#Use the data from sql for the products being sold

#From the tutorial
#Add each of your products to a database.
#Then, when you dynamically create the product page, 
# store the product database ID and price in data attributes within the purchase button.
#Update the /create-checkout-session route to only allow POST requests.
#Update the JavaScript event listener to grab the product info from the data attributes and 
# send them along with the AJAX POST request to the /create-checkout-session route.
#Parse the JSON payload in the route handler and confirm that the product exists and that 
# the price is correct before creating a Checkout Session.
