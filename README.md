# pyjsondatuvizualizacija

## programma, kas lietotājam ļauj ievadīt failus(json + eventlog) un pēctam tos vizualizēs. Izmantojot python(tkint) un svg

### kas izdarīts
Pēdējā mēneša laikā esmu izveidojis šo programmu no nulles. Sākumā fokusējos uz darbu ar JSON failiem – apguvu to struktūru, apstrādes iespējas un kā tos efektīvi izmantot programmā.

Pēc tam pārgāju pie lietotāja interfeisa izstrādes, izmantojot Tkinter. Uzbūvēju atsevišķus logus dažādai funkcionalitātei, lai lietotājam būtu ērti pārvietoties starp datu ievadi, žurnālu pārskatīšanu un vizualizācijām. 

Vienu brīdi radās liela putra - aptuveni 800līnijui kods vienā failā. Prakses vadītājs ieteica to sadalīt pa daļām(vizualizacija,galvenais,uzerinterface u.t.). Tas bija arī liels mācīšanās process man, jo iperikeš nebiju šādi dalījis kodu pa daļām. 

Papildus izveidoju arī vizualizācijas komponenti – tā tiek ielādēta tikai poga nospiešanas gadījumā.

Vizualizacija bija visgrūtākais šajā visā. Pirmoreizi izmantoju svg formātu. To sasaistīt ar kaut kādu loģiku(no backend - galvenais.py) un attēlot bija ļoti grūti, bet manuprāt rezultāts ir labs
Šobrīd programma spēj apvienot json +eventlog failus un pēctam savilkt loģiku un attēlot datu ceļu un errors.

ļoti daudz esmu iemācījies, gan par python, gan svg, gan json, gan tīkliem un to uzbūvi(ip/mac adreses, porti, configuracijas u.t.)

### To do list
Reālistiski, galvenās lietas, ko gribēju pabeigt:

Parādīt pilnu ceļu(no hub uz trafic port) // Veicot navigāciju caur animācijām 'next' 'back', šīs pogas ielikt pašā web browser lai lietotājam būtu ērtāk + izdarīt tā, lai katrai animācijai neielādējas jauna lapa, bet visu rāda vienā.

Laigan pieliku, ka tagad uz disabled(ja tas ir primarry) ceļu nevelk. Tāpat vajadzētu to papildināt un apskatīt kārtīgāk
