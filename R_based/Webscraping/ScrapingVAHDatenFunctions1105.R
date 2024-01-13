library(rvest)
library(tidyverse)
library(xml2)
library(qlcMatrix)
library(openxlsx)

#Hole Daten aus Internet
#1.Basisliste mit NAmen, Hersteller, und Wierkbereich 

url <- "C:/Users/olive/Downloads/VAH-Liste_ VAH-Liste2.html"

#url<-"https://vah-liste.mhp-verlag.de/"
VAHBasis <-  read_html(url) 

VAHBasis <- VAHBasis %>%  html_table(dec=",")

VAHBasis <- VAHBasis[[1]]
VAHBasis<-data.frame(VAHBasis)

#Erstelle Detailseitenlink aus Produktnamen
VAHBasis$simpleprod<-gsub("®","r",VAHBasis[,1])

VAHBasis$simpleprod<-gsub("³ ","3",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("'","",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("™","tm",VAHBasis$simpleprod)
VAHBasis$simpleprod<-tolower(VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("ä","ae",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("ö","oe",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("ü","ue",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("°","",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub(",","",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("\\.","",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("\"","",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("\\(","",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("\\)","",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("& ","",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("&","",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub(" \\+ ","-",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("\\+","-",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub(" - ","-",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("/","-",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("%","-",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub(" ","-",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("---","-",VAHBasis$simpleprod)
VAHBasis$simpleprod<-gsub("--","-",VAHBasis$simpleprod)


#Unregelm??ige Ausnahmen
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="ariel-formula-pro-plus")]<-"ariel-formula-pro")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="aseptomanr-pro")]<-"aseptoman-pro")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="bechtid-premium")]<-"bechtid-pemium")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="bio-sanitas-protect-incl-duftvarianten-zitronenduft-und-rosmarinduft")]<-"bio-sanitas-incl-duftvarianten-zitronenduft-und-rosmarinduft")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="budenatr-intense-d-443")]<-"budenat-intense-d-443")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="dan-klorix-hygienereiniger-original-gruene-frische-lavendel-frische-zitronen-frische")]<-"dan-klorix-hygienereiniger-auch-gruene-frische-lavendelfrische-zitronenfrische")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="dentodermr-sensitive-hd-gel")]<-"dentoderm-sensitive-hd-gel")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="descosept-sensitive-inkl-duftvarianten-lemon-fresh-und-fruit")]<-"descosept-sensitive")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="ec-55")]<-"elma-clean-55d-ec-55")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="ew80-des")]<-"ew-80-des")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="favorit-wet-wipes-bio-xl")]<-"favorit-wet-wipes-bio-xl-neutral-active")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="kanizid-sensitiv-af-neutrallemongrapefruitmelonefresh")]<-"kanizid-sensitiv-af-neutrallemonmelonegrapefruit-himbeere-wildrose-green-apple-fresh")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="manupep-haendedesinfektion")]<-"manupep-haendedesinfekion")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="microsept-fd-in-den-duftvarianten-gruener-apfel-ohne-parfuem-pfirsichbluete")]<-"microsept-fd")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="microsept-fd-quickclean-wipes-inkl-duefte:-neutral-lemon-fresh-melon")]<-"microsept-fd-in-kombination-mit-quick-clean-wipes")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="mikrozid-power-mops")]<-"sumo-disinfect")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="nordtrade-spruehdesinfektion-lemon-neutral-apfel-pfirsich")]<-"nordtrade-spruehdesinfektion-lemon")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="pino-septapin-des-extragrosse-alkoholfreie-tuecher")]<-"pino-septapin-des-extragrosse-tuecher")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="pliwar-lemon-fresh-af-in-den-duftvarianten-gruener-apfel-ohne-parfuem-pfirsichbluete")]<-"pliwar-lemon-fresh-af-in-den-duftvarianten-gruener-apfel-kokos-ohne-parfuem-pfirsichbluete-und-vanille")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="quick-clean-s-wipes-lemon-fresh-und-ohne-parfum")]<-"pliwar-lemon-fresh-af-in-kombination-mit-quick-clean-s-wipes-lemon-fresh")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="sept-liquid-sensitive")]<-"septliquid-sensitive")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="septapin-des-desinfektionstuecher")]<-"pino-septapin-des-desinfektionstuecher")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="ventisept-wipes-rtu-inkl-duftvarianten-pur-honigmelone-pink-grapefruit")]<-"ventisept-wipes-rtu")
try(VAHBasis$simpleprod[which(VAHBasis$simpleprod=="vinkocare-neutral")]<-"vinkocide-hde")


#Bindestriche am Ende l?schen
endings<-str_sub(VAHBasis$simpleprod,start=-1)
replacement<-str_sub(VAHBasis$simpleprod, end = -2)
for(i in 1:nrow(VAHBasis)){
  if(endings[i]=="-"){
    VAHBasis$simpleprod[i]<-replacement[i]
  }
}


#Dopplungen(Produkte mit mehreren Anwendungsbereichen Links haben Zahl als suffix)
doubles<-VAHBasis$simpleprod[which(duplicated(VAHBasis$simpleprod)|duplicated(VAHBasis$simpleprod,fromLast=T)==T)]
suffix<-c(2,0,1,0,1,0,1,0,1,1,2,0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,0,1,0,1,0,1,0,1,0,1,0,1,1,0,0,1)
for(i in 1:length(doubles)){
  if(suffix[i]!=0){
    doubles[i]<-paste(doubles[i],suffix[i],sep="-")
  }
}
#doubles
VAHBasis$simpleprod[which(duplicated(VAHBasis$simpleprod)|duplicated(VAHBasis$simpleprod,fromLast=T)==T)]<-doubles

#Hole Detailseiten
#VAHDetails<-list()
#GetDetails Hole die Detailseiten aus generierten links- Spalte mit Link Suffixes muss simpleprod hei?en
GetDetails<-function(Base=VAHBasis){
  Details<-list()
  for(i in 1:nrow(Base)){
    url<-paste0("https://vah-liste.mhp-verlag.de/suche/details/",Base$simpleprod[i])
    try({temp<-read_html(url);Details[[i]] <-  temp %>%  html_table(dec=",")},silent =T)
  }
  return(Details)
}
VAHDetails<-GetDetails()


#Datenaufbereitung Detailseiten 
#1. Informationen
#Produktinfos an Basistabelle

GetInfos<-function(Base=VAHBasis,Details=VAHDetails){
  Data<-Base
  #VAHDetails2<-VAHDetails
 
  for(j in 1:length(Details)){
    if(length(Details[[j]])>0){
      df<-data.frame(Details[[j]][[1]])
      df[,1]<-gsub(" ","",df[,1])
      df[,1]<-gsub("\\(","",df[,1])
      df[,1]<-gsub("\\)","",df[,1])
      df[,1]<-gsub("/","",df[,1])
      
      for(i in 1:nrow(df)){
        Data[j,df[i,1]]<-df[i,2]
      }
    }
  }
  return(Data)
}
VAH<-GetInfos()


which((VAH$Anwendungsbereich==VAHBasis$Anwendungsbereich)==0)


detailslength<-sapply(VAHDetails,function(x) length(x))

sum(detailslength==2)




####Anwendungstabelle nach anwendungsart
#Anwendungen<-split(VAH,VAH$Anwendungsbereich)


###1.H?ndewaschung
GetHandwaschung<-function(Base=VAH,FullDetails=VAHDetails){
  detailslength<-sapply(FullDetails,function(x) length(x))
  products<-which(Base$Anwendungsbereich=="Händewaschung")
  Handwaschung<-Base[products,]
  counter=1
  for(i in products){
    if(detailslength[i]==3){
      Handwaschung$bakterizid_leuvozid_30s[counter]<-VAHDetails[[i]][[2]][3,2]
      Handwaschung$bakterizid_leuvozid_60s[counter]<-VAHDetails[[i]][[2]][3,3]
    }
    counter<-counter+1
  }
  
  Handwaschung<-Handwaschung[,-c(4,10,12:16)]
  return(Handwaschung)
}
Handwaschung<-GetHandwaschung()
###2.Fl?chendesinfektion

GetFlaecheVAH<-function(Base=VAH,FullDetails=VAHDetails){
  detailslength<-sapply(FullDetails,function(x) length(x))
  products<-which(Base$Anwendungsbereich=="Flächendesinfektion")
  Flaechendesinfektion<-Base[products,]
  counter=1
  
  for(i in products){
    if(detailslength[i]==3){
      Details<-FullDetails[[i]][[2]]
      for(j in 3:nrow(Details)){
        for(k in 2:ncol(Details)){
          Flaechendesinfektion[counter,paste0(Details[j,1],Details[1,k],Details[2,k])]<-Details[j,k]
        }
      }
    }
    counter<-counter+1
  }
  return(Flaechendesinfektion)
}
Flaechendesinfektion<-GetFlaecheVAH()

###3.Haendedesinfektion

GetHaendeDesVAH<-function(Base=VAH,FullDetails=VAHDetails){
  detailslength<-sapply(FullDetails,function(x) length(x))
  products<-which(Base$Anwendungsbereich=="Händedesinfektion")
  Haendedesinfektion<-Base[products,]
  counter=1
  
  for(i in products){
    if(detailslength[i]==3){
      Details<-FullDetails[[i]][[2]]
      for(j in 4:nrow(Details)){
        for(k in 2:ncol(Details)){
          Haendedesinfektion[counter,paste0(Details[j,1],Details[1,k],Details[2,k],Details[3,k])]<-Details[j,k]
        }
      }
    }
    counter<-counter+1
  }
  return(Haendedesinfektion)
}
Haendedesinfektion<-GetHaendeDesVAH()
###4.Hautantiseptik
GetHautVAH<-function(Base=VAH,FullDetails=VAHDetails){
  
  detailslength<-sapply(FullDetails,function(x) length(x))
  products<-which(Base$Anwendungsbereich=="Hautantiseptik")
  Hautantiseptik<-Base[products,]
  counter=1
  
  for(i in products){
    if(detailslength[i]==3){
      Details<-FullDetails[[i]][[2]]
      for(j in 5:nrow(Details)){
        for(k in 2:ncol(Details)){
          Hautantiseptik[counter,paste0(Details[j,1],Details[1,k],Details[2,k],Details[3,k],Details[4,k])]<-Details[j,k]
        }
      }
    }
    counter<-counter+1
  }
  return(Hautantiseptik)
}
Hautantiseptik<-GetHautVAH()

###5.Instrumentendesinfektion
GetInstrumenteVAH<-function(Base=VAH,FullDetails=VAHDetails){
  
  detailslength<-sapply(FullDetails,function(x) length(x))
  products<-which(Base$Anwendungsbereich=="Instrumentendesinfektion")
  Instrumentendesinfektion<-Base[products,]
  counter=1
  for(i in products){
    if(detailslength[i]==3){
      Details<-FullDetails[[i]][[2]]
      for(j in 3:nrow(Details)){
        for(k in 2:ncol(Details)){
          Instrumentendesinfektion[counter,paste0(Details[j,1],Details[1,k],Details[2,k])]<-Details[j,k]
        }
      }
    }
    counter<-counter+1
  }
  return(Instrumentendesinfektion)
}
Instrumentendesinfektion<-GetInstrumenteVAH()

###6.W?sche Desinfektion
GetWaescheVAH<-function(Base=VAH,FullDetails=VAHDetails){
  
  detailslength<-sapply(FullDetails,function(x) length(x))
  products<-which(Base$Anwendungsbereich=="Wäschedesinfektion")
  WaeschedesinfektionVAH<-Base[products,]
  #WaeschedesinfektionVAH %>%
  #  add_column(Anwendungskonzentration=NA,Temperatur_C=NA,Einwirkdauer_min=NA,Flottenverhältnis=NA)
  
  #Temperatur und Einwirkzeit: Maximum ?ber den gesamten Prozess
  counter=1
  for(i in products){
    if(detailslength[i]==3){
      Details<-FullDetails[[i]][[2]]
      temp<-NULL
      temp<-strsplit(as.character(VAHDetails[[i]][[2]][2,2]),"\n")
      temp<-str_trim(temp[[1]],side="both")
      temp<-temp[nzchar(temp)]
      WaeschedesinfektionVAH$Anwendungskonzentration[counter]<-temp[2]
      Temperatur<-temp[3]
      Temperatur<-regmatches(Temperatur, gregexpr("[[:digit:]]+", Temperatur))
      Temperatur<-max(as.numeric(unlist(Temperatur)))
      WaeschedesinfektionVAH$Temperatur_C[counter]<-Temperatur
      Einwirk<-regmatches(temp[4], gregexpr("[[:digit:]]+", temp[4]))
      Einwirk<-max(as.numeric(unlist(Einwirk)))
      WaeschedesinfektionVAH$Einwirkdauer_min[counter]<-Einwirk
      WaeschedesinfektionVAH$Flottenverhältnis[counter]<-strsplit(temp[5]," ")[[1]][2]
    }
    counter<-counter+1
  }

  #Sonderfall Eltra
  WaeschedesinfektionVAH[which(WaeschedesinfektionVAH$simpleprod=="eltra"),18:20]<-NA
  return(WaeschedesinfektionVAH)
}
WaeschedesinfektionVAH<-GetWaescheVAH()


VAHlist<-list("VAH"=VAH,"Handwaschung"=Handwaschung,"Händedesinfektion"=Haendedesinfektion,"Hautantiseptik"=Hautantiseptik
               ,"Flächendesinfektion"=Flaechendesinfektion,"Instrumentendesinfektion"=Instrumentendesinfektion
               ,"Wäschedesinfektion"=WaeschedesinfektionVAH)
write.xlsx(VAHlist, file="VAH.xlsx")

