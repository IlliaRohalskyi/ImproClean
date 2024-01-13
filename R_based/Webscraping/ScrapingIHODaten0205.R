library(rvest)
library(tidyverse)
library(xml2)
library(qlcMatrix)
defaultW <- getOption("warn") 

options(warn = -1) 

url <- "https://www.desinfektionsmittelliste.de/Home/Produktliste/5"

desinfektionsmittelliste <-  read_html(url)
desinfektionsmittelliste <- desinfektionsmittelliste %>%  html_table(dec=",")

#desinfektionsmittelliste <- desinfektionsmittelliste %>% html_nodes(xpath = '//*[@id="ihoProductDataTable"]') %>%  html_table()

desinfektionsmittelliste <- desinfektionsmittelliste[[1]]
df<-data.frame(desinfektionsmittelliste)

Tableprep<-function(df,simplecols=1:7,threesplitcols=8:ncol(df),twosplitcols=5:6,vertsplitcols=8:ncol(df),numcols=NULL,
                    splitchar="\r\n                                            \r\n                                            \r\n",
                    ColNames=c(colnames(df)[1:5],"Einwirkzeit","Flotte","Bakterizide+Leuvurozide","Viruzide","Fungizide"
                               ,"Tuberkulozide","Mykobakterizide")){
  #Split Vertikal
  vecList<-list()
  lengthlist<-matrix(ncol=nrow(df))
  #Vertical Split (getrennte Zellen)
  for(i in vertsplitcols){
    temp<-strsplit(df[,i],splitchar)
    #lengthlist[i-7,]<-lengths(temp)
    lengthtmp<-lengths(temp)
    lengthlist<-rbind(lengthlist,lengthtmp)
    vecList[[i-(vertsplitcols[1]-1)]]<-temp
  }
  #Wie viele Splits für jede ursprüngliche Zeile
  if(nrow(lengthlist)>2){
    Maxlength<-as.numeric(colMax(lengthlist[-1,]))
  } else {
    Maxlength<-lengthlist[-1,]
  }
  Data<-data.frame(rep(NA,sum(Maxlength)))
  #Daten in richtige Form bringen
  for(i in 1:length(vecList)){
    for(j in 1:ncol(lengthlist)){
      if(length(vecList[[i]][[j]])<Maxlength[j]){
        vecList[[i]][[j]]<-c( vecList[[i]][[j]],rep(NA,Maxlength[j]-length(vecList[[i]][[j]])))
      }
    }
    Data[,i]<-unlist(vecList[[i]])
    Data[,i]<-str_trim(Data[,i],side="both")
  }
  #Einfache Spalten wiederholen
  Test<-df[rep(seq_len(nrow(df)), Maxlength),simplecols ]
  Desinfektionsmittel<-cbind(Test,Data)
  colnames(Desinfektionsmittel) <- ColNames
  #Whitespaces
  for (i in 1:ncol(Desinfektionsmittel)){
    Desinfektionsmittel[,i]<- str_trim(Desinfektionsmittel[,i],side="both")
  }
  #Numerische Spalten ohne Zusatzinfo
  if(length(numcols)>0){
    for (i in numcols){
      Desinfektionsmittel[,i]<-as.numeric(gsub(",",".",Desinfektionsmittel[,i]))
    }
  }
  
  #Split horizontal (3Teile) - Messwert - Einheit -Info
  if(length(threesplitcols)>0){
    counter=0
    for (i in threesplitcols){
      Desinfektionsmittel[,i+counter]<-str_trim(Desinfektionsmittel[,i+counter],side="both")
      Desinfektionsmittel<-separate(Desinfektionsmittel,i+counter,into=c(paste(colnames(Desinfektionsmittel)[i+counter],"measureunit"),paste(colnames(Desinfektionsmittel)[i+counter],"Product")),sep=" - ")
      Desinfektionsmittel<-separate(Desinfektionsmittel,i+counter,into=c(paste(colnames(Desinfektionsmittel)[i+counter],"measure"),paste(colnames(Desinfektionsmittel)[i+counter],"unit")),sep=" ")
      Desinfektionsmittel[,i+counter]<-as.numeric(gsub(",",".",Desinfektionsmittel[,i+counter]))
      counter<-counter+2
    }
  }
  #Split horizontal (2Teile) - Messwert -Einheit
  if(length(twosplitcols)>0){
  counter=0
    for (i in twosplitcols){
      Desinfektionsmittel<-separate(Desinfektionsmittel,i+counter,into=c(paste(colnames(Desinfektionsmittel)[i+counter],"measure"),paste(colnames(Desinfektionsmittel)[i+counter],"unit")),sep=" ")
      Desinfektionsmittel[,i+counter]<-as.numeric(gsub(",",".",Desinfektionsmittel[,i+counter]))
      counter<-counter+1
    }
  }
  return(Desinfektionsmittel)
}

WaescheDesinfektion<-Tableprep(df)

##################
url <- "https://www.desinfektionsmittelliste.de/Home/Produktliste/1"

fldesinf_o_M <-  read_html(url)

fldesinf_o_M <- fldesinf_o_M  %>%  html_table(dec=",")

fldesinf_o_M <- fldesinf_o_M[[1]]

fldesinf_o_M<-data.frame(fldesinf_o_M)

List11<-Tableprep(fldesinf_o_M[,1:4],simplecols=1:3,threesplitcols=NULL,twosplitcols=NULL,vertsplitcols=4,numcols=NULL,
                splitchar="\r\n                                \r\n",
                ColNames=c(colnames(fldesinf_o_M)[1:4]))
List12<-Tableprep(fldesinf_o_M[,c(1:3,5)],simplecols=1:3,threesplitcols=NULL,twosplitcols=4,vertsplitcols=4,numcols=NULL,
                  splitchar="\r\n                                    \r\n                                    \r\n",
                  ColNames=c(colnames(fldesinf_o_M)[1:3],"Einwirkzeit"))
List13<-Tableprep(fldesinf_o_M[,c(1:3,6:14)],simplecols=1:3,threesplitcols=NULL,twosplitcols=NULL,vertsplitcols=4:12,numcols=4:12,
                  splitchar="\r\n                                            \r\n                                            \r\n",
                  ColNames=c(colnames(fldesinf_o_M)[1:3],"Bakterizide+Leuvurozide[Konz in%]","Fungizide[Konz in%]","Tuberkulozide[Konz in%]",
                             "Mykobakterizide[Konz in%]","Sporizidie gegen c.difficile[Konz in%]","sporizidie[Konz in%]"," Begrenzte Viruzide[Konz in%]",
                             "Begrenzte Viruzide Plus[Konz in%]","Viruzide[Konz in%]"))

FlaucheohneMech<-cbind(List11,"Einwirkzeit"=List12[,4],List13[,4:12])

############
#Fläche mit

url <- "https://www.desinfektionsmittelliste.de/Home/Produktliste/6"

fldesinf_m_M <-  read_html(url)

fldesinf_m_M <- fldesinf_m_M  %>%  html_table(dec=",")

fldesinf_m_M <- fldesinf_m_M[[1]]

fldesinf_m_M<-data.frame(fldesinf_m_M)

List61<-Tableprep(fldesinf_m_M[,1:4],simplecols=1:3,threesplitcols=NULL,twosplitcols=NULL,vertsplitcols=4,numcols=NULL,
                  splitchar="\r\n                                \r\n",
                  ColNames=c(colnames(fldesinf_m_M)[1:4]))
List62<-Tableprep(fldesinf_m_M[,c(1:3,5)],simplecols=1:3,threesplitcols=NULL,twosplitcols=4,vertsplitcols=4,numcols=NULL,
                  splitchar="\r\n                                    \r\n                                    \r\n",
                  ColNames=c(colnames(fldesinf_m_M)[1:3],"Einwirkzeit"))
List63<-Tableprep(fldesinf_m_M[,c(1:3,6:14)],simplecols=1:3,threesplitcols=NULL,twosplitcols=NULL,vertsplitcols=4:12,numcols=4:12,
                  splitchar="\r\n                                            \r\n                                            \r\n",
                  ColNames=c(colnames(fldesinf_m_M)[1:3],"Bakterizide+Leuvurozide[Konz in%]","Fungizide[Konz in%]","Tuberkulozide[Konz in%]",
                             "Mykobakterizide[Konz in%]","Sporizidie gegen c.difficile[Konz in%]","sporizidie[Konz in%]"," Begrenzte Viruzide[Konz in%]",
                             "Begrenzte Viruzide Plus[Konz in%]","Viruzide[Konz in%]"))

FlaechemitMech<-cbind(List61,"Einwirkzeit"=List62[,4],List63[,4:12])


############
#Instrumente Manuell

url <- "https://www.desinfektionsmittelliste.de/Home/Produktliste/2"

InstrumenteManual <-  read_html(url)

InstrumenteManual <- InstrumenteManual  %>%  html_table(dec=",")

InstrumenteManual <- InstrumenteManual[[1]]

InstrumenteManual<-data.frame(InstrumenteManual)

List21<-Tableprep(InstrumenteManual[,1:4],simplecols=1:3,threesplitcols=NULL,twosplitcols=NULL,vertsplitcols=4,numcols=NULL,
                  splitchar="\r\n                                \r\n",
                  ColNames=c(colnames(InstrumenteManual)[1:4]))
List22<-Tableprep(InstrumenteManual[,c(1:3,5)],simplecols=1:3,threesplitcols=NULL,twosplitcols=4,vertsplitcols=4,numcols=NULL,
                  splitchar="\r\n                                    \r\n                                    \r\n",
                  ColNames=c(colnames(InstrumenteManual)[1:3],"Einwirkzeit"))
List23<-Tableprep(InstrumenteManual[,c(1:3,6:13)],simplecols=1:3,threesplitcols=NULL,twosplitcols=NULL,vertsplitcols=4:11,numcols=4:11,
                  splitchar="\r\n                                            \r\n                                            \r\n",
                  ColNames=c(colnames(InstrumenteManual)[1:3],"Bakterizide+Leuvurozide[Konz in%]","Fungizide[Konz in%]","Tuberkulozide[Konz in%]",
                             "Mykobakterizide[Konz in%]","Sporizidie gegen c.difficile[Konz in%]","sporizidie[Konz in%]"," Begrenzte Viruzide[Konz in%]",
                             "Viruzide[Konz in%]"))

InstrumenteManuell<-cbind(List21,"Einwirkzeit"=List22[,4],List23[,4:11])


############
#Instrumente Maschinell

url <- "https://www.desinfektionsmittelliste.de/Home/Produktliste/3"

InstrumenteMasch <-  read_html(url)

InstrumenteMasch <- InstrumenteMasch  %>%  html_table(dec=",")

InstrumenteMasch <- InstrumenteMasch[[1]]

InstrumenteMasch<-data.frame(InstrumenteMasch)

List31<-Tableprep(InstrumenteMasch[,c(1:3,4,6)],simplecols=1:3,threesplitcols=NULL,twosplitcols=4:5,vertsplitcols=4:5,numcols=NULL,
                  splitchar="\r\n                                    \r\n                                    \r\n",
                  ColNames=c(colnames(InstrumenteMasch)[1:4],"Einwirkzeit"))
List32<-Tableprep(InstrumenteMasch[,c(1:3,5)],simplecols=1:3,threesplitcols=NULL,twosplitcols=NULL,vertsplitcols=4,numcols=NULL,
                  splitchar="\r\n                                \r\n",
                  ColNames=c(colnames(InstrumenteMasch)[c(1:3,5)]))
List33<-Tableprep(InstrumenteMasch[,c(1:3,7:14)],simplecols=1:3,threesplitcols=NULL,twosplitcols=NULL,vertsplitcols=4:11,numcols=4:11,
                  splitchar="\r\n                                            \r\n                                            \r\n",
                  ColNames=c(colnames(InstrumenteMasch)[1:3],"Bakterizide+Leuvurozide[Konz in%]","Fungizide[Konz in%]","Tuberkulozide[Konz in%]",
                             "Mykobakterizide[Konz in%]","Sporizidie gegen c.difficile[Konz in%]","sporizidie[Konz in%]"," Begrenzte Viruzide[Konz in%]",
                             "Viruzide[Konz in%]"))

InstrumenteMaschinell<-cbind(List32,List31[,4:7],List33[,4:11])

options(warn = defaultW)

IHOlist<-list("Wäschedesinfektion"=WaescheDesinfektion,"FlächendesinfektionMitMechanik"=FlaechemitMech
              ,"FlächendesinfektionOhneMechanik"=FlaucheohneMech,"InstrumentendesManuell"=InstrumenteManuell
              ,"InstrumentendesMaschinell"=InstrumenteMaschinell)
write.xlsx(IHOlist, file="IHO.xlsx")
