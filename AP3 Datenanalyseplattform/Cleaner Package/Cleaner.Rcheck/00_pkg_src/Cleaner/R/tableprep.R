library(rvest)
library(tidyverse)
library(xml2)
library(qlcMatrix)

# url <- "https://www.desinfektionsmittelliste.de/Home/Produktliste/5"
#
# desinfektionsmittelliste <-  read_html(url)
# desinfektionsmittelliste <- desinfektionsmittelliste %>%  html_table(dec=",")
#
# #desinfektionsmittelliste <- desinfektionsmittelliste %>% html_nodes(xpath = '//*[@id="ihoProductDataTable"]') %>%  html_table()
#
# desinfektionsmittelliste <- desinfektionsmittelliste[[1]]
# df<-data.frame(desinfektionsmittelliste)


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
  #Wie viele Splits f?r jede urspr?ngliche Zeile
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
