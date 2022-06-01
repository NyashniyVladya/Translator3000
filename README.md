# Translator3000. Trial version.

### Automatic translator of games made on Ren'Py engine.

<br>

<div id="imageLinks" align="left">
    <a href="https://boosty.to/nyashniyvladya"><img src="https://user-images.githubusercontent.com/19994753/171388249-2dd82009-e065-4435-af0b-5b198478cedb.png" height="50" alt="Support with Boosty"/></a>
    <a href="https://www.patreon.com/bePatron?u=62209932"><img src="https://user-images.githubusercontent.com/19994753/154846762-2cd02dfb-a281-4d30-806a-45bd199001eb.png" height="55" alt="Support with Patreon"/></a>
    <a href="https://discord.gg/FqsQXNH6Fg"><img src="https://user-images.githubusercontent.com/19994753/154846983-4c1294dd-e000-4c87-94fa-ac4943f6bd2f.png" height="50" alt="Join Discord community"/></a>
</div>

<br>

<a href="https://boosty.to/nyashniyvladya"><img src="https://user-images.githubusercontent.com/19994753/171388249-2dd82009-e065-4435-af0b-5b198478cedb.png" height="15" alt="Support with Boosty"/></a> [Download main version from Boosty](https://boosty.to/nyashniyvladya)

<a href="https://www.patreon.com/bePatron?u=62209932"><img src="https://user-images.githubusercontent.com/19994753/154846762-2cd02dfb-a281-4d30-806a-45bd199001eb.png" height="15" alt="Support with Patreon"/></a> [Download main version from Patreon](https://www.patreon.com/bePatron?u=62209932)

<a href="https://discord.gg/FqsQXNH6Fg"><img src="https://user-images.githubusercontent.com/19994753/154846983-4c1294dd-e000-4c87-94fa-ac4943f6bd2f.png" height="15" alt="Join Discord community"/></a> [Join Discord community](https://discord.gg/FqsQXNH6Fg)

<br>

[Instruction manual and compiled *.rpa* file for use in games.](https://github.com/NyashniyVladya/Translator3000/releases)

*Works in games made on Ren'Py 6.99.12.4 and newer.*

<br>

<details>
<summary>
    FAQ (English)
</summary>

1. **I have "squares" instead of text.**
    * *Change the font to one that supports the characters of the language you want.*
        * *Instructions for installing fonts can be found on the releases page.*
        * **Where can I find the fonts?**
           * *By the search query "fonts download" in any search engine.*

1. **The game ***\<insert game name\>*** does not translate (or does not start), although the other games are fine.**
    * *How a game is made depends on the developer. Depending on the implementation, there may be conflicts in individual games. Get over it. There's nothing I can do here. Compatibility with all games in the universe, unfortunately, can not be realized.*

1. **With the translator the game starts to "freeze".**
    * *Translation takes place in real time. It takes some time to send a request, process the response and output the text. And freezes, when reading new phrases for the first time, are inevitable. When reading the same phrases again, there will be no freezes, because translations are cached.*

1. **How do I open the graphical translator interface?**
    * _***Alt***+***~*** (tilde) key combination._
        * *A combination is a simultaneous pressing of two or more keys.*
    1. **Why such a strange key choice?**
        * *Because of the compatibility issue. I try to make the translator as universal as possible, and this combination is unlikely to be used in any game.*
    1. **Can it be changed?**
        * *Maybe someday... But... Why?.. At this point, as far as I know, there has never been a conflict of key combinations in games, which means the choice is the right one.*

1. **The translator removes tags from the original game (italic, bold, color, etc.).**
    * _Yep. It also removes text tags like ***{w}***/***{nw}*** and the like._
    * *I did this because tags cannot be escaped when accessing a translation service.*
       *For a request ***"{color=...}"*** the service may well return ***"{цвет=...}"*** (for example), which, of course, will lead to an error.*
       *Sure, it is possible to translate in parts (a fragment before the tag, a fragment after it, etc.), but in this case the quality of translation will suffer, because words will be translated without taking into account all the context and will not be connected to each other.*
       *I see no way to "painlessly" preserve the tags, so I decided to remove them altogether.*

1. **How do I run the translator on Android?**
    * *Idk. I write the translator for the PC version. I have never coded for phones and do not know how to do it.*
    * *As far as I heard, there seem to be some ports from third-party developers, but I have nothing to do with them. Use them only at your own risk.*

1. **After reading this post, I still have a question!**
    * _Your question has probably already been asked. Please take a look at the [Issues section](https://github.com/NyashniyVladya/Translator3000/issues), and don't forget to check the "closed" tab for questions that have already been answered._

</details>


<details>
<summary>
    Ответы на частые вопросы (На русском)
</summary>

1. **У меня "квадратики" вместо текста.**
    * *Смените шрифт на другой, поддерживающий нужный Вам язык.*
        * *Инструкция по установке шрифта находится на странице релизов.*
        * **Где я могу найти шрифты?**
           * *По запросу "шрифты скачать" в любом поисковике.*

1. **Игра ***\<вставить имя игры\>*** не переводится (или не запускается).**
    * *Как сделана та или иная игра зависит от разработчика. В зависимости от реализации, могут быть конфликты в отдельных играх. Смиритесь. Здесь я ничего не могу поделать. Совместимость со всеми играми во вселенной реализовать, к сожалению, не получится.*

1. **С переводчиком игра начинает "подвисать" / "подлагивать" / "фризить".**
    * *Перевод происходит в реальном времени. На отправку запросу запроса, обработку ответа и вывод текста тратится некоторое время. И лаги, при первом чтении новых фраз, неизбежны. При повторном прочтении этих же самых мест, лагов не будет, т.к. переводы кэшируются.*

1. **Как вызвать графический интерфейс переводчика?**
    * _Комбинация (одновременное нажатие) клавиш ***Alt***+***~*** (тильда)._
    1. **Почему такой странный выбор?**
        * *Из за вопроса совместимости. Я стараюсь делать переводчик наиболее универсальным, а такую комбинацию вряд ли где будут использовать.*
    1. **Можно поменять?**
        * *Some day... Some time... На данный момент, насколько я знаю, ни разу не было конфликтов комбинаций с играми, а значит выбор верный.*

1. **Переводчик удаляет теги из оригинальной игры (курсив, жирный текст, цвет и прочее).**
    * _Есть такое. А ещё удаляет текстовые теги вида ***{w}***/***{nw}*** и подобные._
    * *Сделано это потому что теги нельзя экранировать, при обращении к сервису перевода.*
       *На ***"{color=...}"*** сервис вполне может вернуть ***"{цвет=...}"***, что, разумеется, приведёт к ошибке.*
       *Можно, конечно, переводить частями (отрывок до тега, отрывок после него и т.д.), но в этом случае сильно пострадает качество самого перевода, т.к. слова переведутся без учёта всего контекста и будут не связаны между собой.*
       *Я не вижу способа "безболезненно" сохранить теги, поэтому принял решение убрать их вообще.*

1. **А как запустить переводчик на ОС Android?**
    * *Без понятия. Переводчик я пишу под ПК версию. Под телефоны никогда не прогал и не умею этого делать.*
    * *Насколько я слышал, вроде бы существуют какие-то порты от сторонних разработчиков, но я к ним отношения не имею. Пользуйтесь ими только на свой страх и риск.*

1. **После прочтения этого поста у меня всё ещё остался вопрос!**
    * _Скорее всего, его уже задавали. Посмотрите, пожалуйста, [раздел Issues](https://github.com/NyashniyVladya/Translator3000/issues) и не забудьте заглянуть на вкладку "closed", где находятся решённые вопросы._

</details>
