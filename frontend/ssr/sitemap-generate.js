const XMLBuilder = require('xmlbuilder');

const FS = require('fs');

const axios = require('axios');

var doc = XMLBuilder.create('urlset');
doc.att('xmlns', 'http://www.sitemaps.org/schemas/0.9');
doc.ele('url').ele('loc').text('https://dari-cosmetics.ru')
    .up()
    .ele('lastmod').text(new Date().toISOString().substr(0,10))
    .up()
    .ele('changefreq').text('weekly')
    .up()
    .ele('priority').text('1.0')
    .up()
.up()

const getProds = async () => {
    try {
        return await axios.get('https://dari-cosmetics.ru/api/shop/catalog')
    } catch (error) {
        console.log(error);
    }
}

const getProgs = async () => {
    try {
        return await axios.get('https://dari-cosmetics.ru/api/shop/kits?limit=100')
    } catch (err) {
        console.log(err);
    }
}

const getBlog = async () => {
    try {
        return await axios.get('https://dari-cosmetics.ru/api/blog/articles?limit=100')
    } catch (er) {
        console.log(er)
    }
}

const writeMap = async () => {
    const categories = await getProds();
    if (categories.data) {
        const cats = categories.data;
        cats.forEach(catItem => {
            catItem.subcats.forEach(subcatItem => {
                subcatItem.subcat_products.forEach(prod => {
                    doc.ele('url').ele('loc').text('https://dari-cosmetics.ru/catalog/' + catItem.slug + '/' + subcatItem.slug + '/' + prod.slug)
                    .up()                    
                    .ele('lastmod').text(new Date().toISOString().substr(0,10))
                    .up()
                    .ele('changefreq').text('weekly')
                    .up()
                    .ele('priority').text('0.9')
                    .up()
                    .up()
                })
            })
        })
    }
}

const writeProgramsMap = async () => {
    const progs = await getProgs();
    if (progs.data) {
        progs.data.results.forEach(prog => {
            doc.ele('url').ele('loc').text('https://dari-cosmetics.ru/care-program/' + prog.slug)
            .up()                    
            .ele('lastmod').text(new Date().toISOString().substr(0,10))
            .up()
            .ele('changefreq').text('weekly')
            .up()
            .ele('priority').text('0.9')
            .up()
            .up()
        })
    }
}

const writeBlogMap = async () => {
    const arts = await getBlog();
    if (arts.data.results) {
        arts.data.results.forEach(art => {
            doc.ele('url').ele('loc').text('https://dari-cosmetics.ru/blog/' + art.slug)
            .up()                    
            .ele('lastmod').text(new Date().toISOString().substr(0,10))
            .up()
            .ele('changefreq').text('weekly')
            .up()
            .ele('priority').text('0.5')
            .up()
            .up()
        })
    }
    FS.writeFileSync('sitemap.xml', doc.toString());
    console.log('end');
}

writeMap().then(() => {
    writeProgramsMap().then(() => {
        writeBlogMap();
    });
});
