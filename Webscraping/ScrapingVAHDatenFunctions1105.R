library(rvest)
library(tidyverse)
library(xml2)
library(qlcMatrix)
library(openxlsx)

#Hole Daten aus Internet
#1.Basisliste mit NAmen, Hersteller, und Wierkbereich 

url <- "C:/Users/olive/Downloads/VAH-Liste_ VAH-Liste.html"

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
VAHBasis$simpleprod[80]<-"ariel-formula-pro"
VAHBasis$simpleprod[88]<-"aseptoman-pro"
VAHBasis$simpleprod[128]<-"bechtid-pemium"
VAHBasis$simpleprod[157]<-"bio-sanitas-incl-duftvarianten-zitronenduft-und-rosmarinduft"
VAHBasis$simpleprod[175]<-"budenat-intense-d-443"
VAHBasis$simpleprod[266]<-"dan-klorix-hygienereiniger-auch-gruene-frische-lavendelfrische-zitronenfrische"
VAHBasis$simpleprod[301]<-"dentoderm-sensitive-hd-gel"
VAHBasis$simpleprod[329]<-"descosept-sensitive"
VAHBasis$simpleprod[410]<-"elma-clean-55d-ec-55"
VAHBasis$simpleprod[434]<-"ew-80-des"
VAHBasis$simpleprod[452]<-"favorit-wet-wipes-bio-xl-neutral-active"
VAHBasis$simpleprod[663]<-"kanizid-sensitiv-af-neutrallemonmelonegrapefruit-himbeere-wildrose-green-apple-fresh"
VAHBasis$simpleprod[745]<-"manupep-haendedesinfekion"
VAHBasis$simpleprod[800]<-"microsept-fd"
VAHBasis$simpleprod[801]<-"microsept-fd-in-kombination-mit-quick-clean-wipes"
VAHBasis$simpleprod[809]<-"sumo-disinfect"
VAHBasis$simpleprod[864]<-"nordtrade-spruehdesinfektion-lemon"
VAHBasis$simpleprod[978]<-"pino-septapin-des-extragrosse-tuecher"
VAHBasis$simpleprod[984]<-"pliwar-lemon-fresh-af-in-den-duftvarianten-gruener-apfel-kokos-ohne-parfuem-pfirsichbluete-und-vanille"
VAHBasis$simpleprod[1047]<-"pliwar-lemon-fresh-af-in-kombination-mit-quick-clean-s-wipes-lemon-fresh"
VAHBasis$simpleprod[1148]<-"septliquid-sensitive"
VAHBasis$simpleprod[1152]<-"pino-septapin-des-desinfektionstuecher"
VAHBasis$simpleprod[1322]<-"ventisept-wipes-rtu"
VAHBasis$simpleprod[1330]<-"vinkocide-hde"

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
Anwendungen<-split(VAH,VAH$Anwendungsbereich)


###1.H?ndewaschung
Handwaschung<-Anwendungen$Händewaschung
Handwaschung %>%
  add_column(bakterizid_leuvozid_30s=NA,bakterizid_leuvozid_60s=NA)

products<-which(VAH$Anwendungsbereich=="Händewaschung")
counter=1
for(i in products){
  if(detailslength[i]==3){
    Handwaschung$bakterizid_leuvozid_30s[counter]<-VAHDetails[[i]][[2]][3,2]
    Handwaschung$bakterizid_leuvozid_60s[counter]<-VAHDetails[[i]][[2]][3,3]
  }
  counter<-counter+1
}

Handwaschung<-Handwaschung[,-c(4,10,12:16)]


###2.Fl?chendesinfektion

Flaechendesinfektion<-Anwendungen$Flächendesinfektion
#Flaechendesinfektion %>%
 # add_column(bakterizid_leuvozid_30s=NA,
#             bakterizid_leuvozid_60s=NA)

products<-which(VAH$Anwendungsbereich=="Flächendesinfektion")
counter=1

for(i in products){
  if(detailslength[i]==3){
    Details<-VAHDetails[[i]][[2]]
    for(j in 3:nrow(Details)){
      for(k in 2:ncol(Details)){
        Flaechendesinfektion[counter,paste0(Details[j,1],Details[1,k],Details[2,k])]<-Details[j,k]
      }
    }
  }
  counter<-counter+1
}


###3.Haendedesinfektion
Haendedesinfektion<-Anwendungen$Händedesinfektion

products<-which(VAH$Anwendungsbereich=="Händedesinfektion")
counter=1

for(i in products){
  if(detailslength[i]==3){
    Details<-VAHDetails[[i]][[2]]
    for(j in 4:nrow(Details)){
      for(k in 2:ncol(Details)){
        Haendedesinfektion[counter,paste0(Details[j,1],Details[1,k],Details[2,k],Details[3,k])]<-Details[j,k]
      }
    }
  }
  counter<-counter+1
}

###4.Hautantiseptik
Hautantiseptik<-Anwendungen$Hautantiseptik

products<-which(VAH$Anwendungsbereich=="Hautantiseptik")
counter=1

for(i in products){
  if(detailslength[i]==3){
    Details<-VAHDetails[[i]][[2]]
    for(j in 5:nrow(Details)){
      for(k in 2:ncol(Details)){
        Hautantiseptik[counter,paste0(Details[j,1],Details[1,k],Details[2,k],Details[3,k],Details[4,k])]<-Details[j,k]
      }
    }
  }
  counter<-counter+1
}


###5.Instrumentendesinfektion
Instrumentendesinfektion<-Anwendungen$Instrumentendesinfektion

products<-which(VAH$Anwendungsbereich=="Instrumentendesinfektion")
counter=1

for(i in products){
  if(detailslength[i]==3){
    Details<-VAHDetails[[i]][[2]]
    for(j in 3:nrow(Details)){
      for(k in 2:ncol(Details)){
        Instrumentendesinfektion[counter,paste0(Details[j,1],Details[1,k],Details[2,k])]<-Details[j,k]
      }
    }
  }
  counter<-counter+1
}

###6.W?sche Desinfektion
WaeschedesinfektionVAH<-Anwendungen$Wäschedesinfektion

products<-which(VAH$Anwendungsbereich=="Wäschedesinfektion")

WaeschedesinfektionVAH %>%
  add_column(Anwendungskonzentration=NA,Temperatur_C=NA,Einwirkdauer_min=NA,Flottenverhältnis=NA)

#Temperatur und Einwirkzeit: Maximum ?ber den gesamten Prozess
counter=1
for(i in products){
  if(detailslength[i]==3){
    Details<-VAHDetails[[i]][[2]]
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


VAHlist<-list("VAH"=VAH,"Handwaschung"=Handwaschung,"Händedesinfektion"=Haendedesinfektion,"Hautantiseptik"=Hautantiseptik
               ,"Flächendesinfektion"=Flaechendesinfektion,"Instrumentendesinfektion"=Instrumentendesinfektion
               ,"Wäschedesinfektion"=WaeschedesinfektionVAH)
write.xlsx(VAHlist, file="VAH.xlsx")

