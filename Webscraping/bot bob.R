#remotes::install_github("ropensci/RSelenium")
#docker run -d -p 4445:4444 selenium/standalone-firefox:2.53.0
#docker ps
library(RSelenium)
library(rvest)
library(tidyr)
remDr <- RSelenium::remoteDriver(remoteServerAddr = "localhost",
                                 port = 4445L,
                                 browserName = "firefox")
remDr$open()


remDr$navigate("https://vah-liste.mhp-verlag.de/")
remDr$findElements("id", "lnsvah_simplesubmit")[[1]]$clickElement()
Sys.sleep(10) 

html <- remDr$getPageSource()[[1]]
table <- read_html(html)
table <- rvest::html_elements(table, xpath='//*[@id="c53"]/div/div/div[2]/div/div/div/div/div/div/div[2]/table')
table <- html_table(table,dec=",",fill=T)
table[[1]][3]
remDr$screenshot(display = TRUE)


remDr$close()




















# Agree_button <- remote_driver$findElement(using = 'id', value = "btAgree")
# Agree_button$clickElement()
# remDr$navigate("https://vah-liste.mhp-verlag.de/")

# read_html(html) %>% 
#   html_nodes("table") %>% 
#   html_attr("onclick")

