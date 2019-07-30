<!-- PROJECT SHIELDS -->  
[![Contributors][contributors-shield]][contributors-url]  
[![Forks][forks-shield]][forks-url]  
[![Stargazers][stars-shield]][stars-url]  
[![Issues][issues-shield]][issues-url]  
[![MIT License][license-shield]][license-url]  
  
  
  
<!-- PROJECT LOGO -->  
<br />  
<p align="center">  
 <a href="https://github.com/anguyen120/fake-news-in-time">  
  <img src="https://i.imgur.com/a2uqTFz.png" alt="Logo" width="80" height="80">
 </a> <h3 align="center">Fake News in Time</h3>  
  
 <p align="center">  
    Analysis of fake news language evolution in time  
    <br />  
 <a href="https://github.com/github_username/fake-news-in-time/issues">Report Bug</a>  
    ·  
    <a href="https://github.com/anguyen120/fake-news-in-time/issues">Request Feature</a>  
 </p></p>  

  
  
<!-- TABLE OF CONTENTS -->  
## Table of Contents  
  
* [About the Project](#about-the-project)  
	* [Built With](#built-with)  
* [Getting Started](#getting-started)  
	* [Prerequisites](#prerequisites)  
	* [Installation](#installation)  
* [Usage](#usage)  
* [Roadmap](#roadmap)  
* [Contributing](#contributing)  
* [License](#license)  
* [Contact](#contact)  
* [Acknowledgements](#acknowledgements)  
  
  
  
<!-- ABOUT THE PROJECT -->  
## About The Project  
  
As part of Texas A&M -- University of Cyprus Student Exchange Program, this is a research internship project for Summer 2019. As the technology evolved to stop the propagation of fake news, the propagandists and the people that deliberately share false content adapted. Analyzing evolution of fake news' language provides new cues in determining fake news.

Due to the fact that several fake news articles might have been removed from the web, this project utilizes [Web Archive's](https://web.archive.org/) snapshots, where webpages are available overtime.

The project has been devised into three steps:    

![Process Image][process-image]  

1.  **Data Crawling and Web Scraping** 
	* Using the [Scrapy](https://scrapy.org/)  framework, the project breaks down this process into two crawlers:
		*  `cdx.py spider`
			* This collects valid snapshots from [Wayback CDX Server API](https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server). It deploys crawlers to the snapshot urls to extract urls from the page using Scrapy's link extractor. After collecting urls, it inserts the data into MongoDB.
		*  `url_spider.py spider`
			* This must start off by making aggregations to the urls collection (default in `config.py`) in MongoDB. It then filters the aggregated urls and parse the article by using the [Newspaper3k](https://newspaper.readthedocs.io/en/latest/) library. The spider inserts the articles' metadata into an article collection or filter collection.
		* *One could avoid using the separated crawlers by using* `article.py spider`*, which is a combination of the two spiders. It is able to both collect and filter urls from Wayback CDX Server API snapshots then crawl the articles' url. It avoids the insertions in urls collection. (At this time, it has not been fully tested for functionality.)*
2.  **Text Analytics and Natural Language Processing (NLP)**
	* This project employs Check-It's<sup>1</sup> feature engineering component. It divides linguistic features into:
		1. Part-of-Speech
		2. Readability and Vocabulary Richness
		3. Sentiment Analysis
		4. Surface and Syntax
		5. Punctuation
	* *Currently, the code for the feature engineering is not publicly available, but this repository will update when it has become available. For now, this [article's](https://www.analyticsvidhya.com/blog/2018/02/the-different-methods-deal-text-data-predictive-python/) sentiment analysis section provides an alternative to Check-It's* sentiment score.
3.  **Statistical Analysis on Time-series Data** 
	* This process takes in the outputted CVS file based from the extracted features from the previous step. By using [pandas](https://pandas.pydata.org/) library to convert the CVS file into a data frame, [Matplotlib](https://matplotlib.org/) and [seaborn](https://seaborn.pydata.org/) library handles plotting the data into a time-series graphs. To make statistical analysis from the plots, one must apply their knowledge and intuition to approach a conclusion. 

Essentially, the main purpose of this project is the data crawling and web scraping component for future work though.

<sup>1</sup> Paschalides et al. (2019) Demetris Paschalides, Alexandros Kornilakis, Chrysovalantis Christodoulou, Rafael Andreou, George Pallis, Marios D. Dikaiakos, and Evangelos Markatos. 2019. Check-It: A Plugin for Detecting and Reducing the Spread of Fake News and Misinformation on the Web. arXiv:1412.6980 https://arxiv.org/abs/1905.04260v1
  
### Built With  
  
* [Scrapy](https://scrapy.org/)  



<!-- GETTING STARTED -->  
## Getting Started  
  
To get a local copy up and running follow these simple steps.  
  
### Prerequisites  

* [MongoDB](https://docs.mongodb.com/manual/installation/)  
* [pip](https://pip.pypa.io/en/stable/installing/)  



### Installation  
  
1. Clone the repo  
```sh  
git clone https://github.com/anguyen120/fake-news-in-time.git  
```
2. Go inside the repo folder
```sh  
cd /folder/to/fake-news-in-time
```
3. Install pip packages  
```sh  
pip3 install -r requirements.txt
```  


    
<!-- USAGE EXAMPLES -->  
## Usage  
  
This portion will be updated to describe guidance about running the application.
  


<!-- ROADMAP -->  
## Roadmap  
  
See the [open issues](https://github.com/anguyen120/fake-news-in-time/issues) for a list of proposed features (and known issues).  
  
  
  
<!-- CONTRIBUTING -->  
## Contributing  
  
Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.  
  
1. Fork the Project  
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)  
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)  
4. Push to the Branch (`git push origin feature/AmazingFeature`)  
5. Open a Pull Request  
  
  
  
<!-- LICENSE -->  
## License  
  
Distributed under the MIT License. See `LICENSE` for more information.  
  
  
  
<!-- CONTACT -->  
## Contact  
  
Alan Nguyen - anguyen120@protonmail.com  
  
Project Link: [https://github.com/anguyen120/fake-news-in-time](https://github.com/anguyen120/fake-news-in-time)  
  
  
  
<!-- ACKNOWLEDGEMENTS -->  
## Acknowledgements  
  
* [Demetris "Jimmy" Paschalides](https://github.com/dpasch01)  
* [LInC](http://linc.ucy.ac.cy/)  
* [www.flaticon.com](www.flaticon.com)
	* Web free icon made by [Pixelmeetup](https://www.flaticon.com/authors/pixelmeetup) from [www.flaticon.com](www.flaticon.com) is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/)
	* Network free icon made by [Smashicons](https://www.flaticon.com/authors/smashicons) from [www.flaticon.com](www.flaticon.com) is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/)
	* Statistics free icon made by [Eucalyp](https://www.flaticon.com/authors/eucalyp) from [www.flaticon.com](www.flaticon.com) is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/)
  
  

  
  
<!-- MARKDOWN LINKS & IMAGES -->  
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->  
[contributors-shield]: https://img.shields.io/github/contributors/anguyen120/fake-news-in-time.svg?style=flat-square  
[contributors-url]: https://github.com/anguyen120/fake-news-in-time/graphs/contributors  
[forks-shield]: https://img.shields.io/github/forks/anguyen120/fake-news-in-time.svg?style=flat-square  
[forks-url]: https://github.com/anguyen120/fake-news-in-time/network/members  
[stars-shield]: https://img.shields.io/github/stars/anguyen120/fake-news-in-time.svg?style=flat-square  
[stars-url]: https://github.com/anguyen120/fake-news-in-time/stargazers  
[issues-shield]: https://img.shields.io/github/issues/anguyen120/fake-news-in-time.svg?style=flat-square  
[issues-url]: https://github.com/anguyen120/fake-news-in-time/issues  
[license-shield]: https://img.shields.io/github/license/anguyen120/fake-news-in-time.svg?style=flat-square  
[license-url]: https://github.com/anguyen120/fake-news-in-time/blob/master/LICENSE.txt  
[process-image]: https://i.imgur.com/DZSLXPe.png
 
