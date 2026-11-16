const fs = require('fs');
const path = require('path');
let seed=20261115;
function rand(){ seed=(seed*1664525+1013904223)>>>0; return seed/4294967296; }
function pick(a){return a[Math.floor(rand()*a.length)];}
const events=[];
const users=Array.from({length:620},(_,i)=>`demo_user_${String(i+1).padStart(4,'0')}`);
const products=[['P-101','Canvas Tote',24],['P-102','Travel Mug',18],['P-103','Desk Lamp',42],['P-104','Wireless Mouse',29],['P-105','Notebook Set',12],['P-106','Bluetooth Speaker',56],['P-107','Phone Stand',16],['P-108','Water Bottle',21],['P-109','USB-C Hub',39],['P-110','Reading Light',14]];
const channels=['Organic Search','Paid Search','Email','Social','Direct','Referral / Other'];
const countries=['United States','United Kingdom','Canada','Australia','India'];
const devices=['desktop','mobile','tablet'];
const start=new Date('2020-11-01T00:00:00Z');
const firstVisitSeen=new Set();
const isoDate=d=>d.toISOString().slice(0,10);
function emit(d,event,user,sid,channel,country,device,tx,item,qty,price){events.push({event_date:isoDate(d),event_timestamp:d.toISOString(),event_name:event,user_pseudo_id:user,session_id:sid,channel,country,device_category:device,transaction_id:tx,item_id:item?.[0]||'',item_name:item?.[1]||'',quantity:qty||0,price:price||0,currency:'USD'});}
for(let s=0;s<1900;s++){
  const user=pick(users), day=Math.floor(rand()*92), date=new Date(start.getTime()+day*86400000+Math.floor(rand()*86400000));
  const sid=`${user}_s${s+1}`, channel=pick(channels), country=pick(countries), device=pick(devices);
  emit(date,'session_start',user,sid,channel,country,device,'',null,0,0);
  if(!firstVisitSeen.has(user)){emit(new Date(date.getTime()+12000),'first_visit',user,sid,channel,country,device,'',null,0,0);firstVisitSeen.add(user);}
  const product=pick(products);
  emit(new Date(date.getTime()+30000),'view_item',user,sid,channel,country,device,'',product,0,product[2]);
  if(rand()<.36){emit(new Date(date.getTime()+65000),'add_to_cart',user,sid,channel,country,device,'',product,1,product[2]);
    if(rand()<.62){emit(new Date(date.getTime()+100000),'begin_checkout',user,sid,channel,country,device,'',product,1,product[2]);
      if(rand()<.43){const tx=`TX-${String(s+1).padStart(6,'0')}`;const count=rand()<.23?2:1;
        for(let j=0;j<count;j++){const it=j?pick(products):product;emit(new Date(date.getTime()+150000+j*1000),'purchase',user,sid,channel,country,device,tx,it,1,it[2]);}
      }
    }
  }
}
const header=['event_date','event_timestamp','event_name','user_pseudo_id','session_id','channel','country','device_category','transaction_id','item_id','item_name','quantity','price','currency'];
const q=v=>`"${String(v??'').replaceAll('"','""')}"`;
const csv=[header.join(','),...events.map(e=>header.map(h=>q(e[h])).join(','))].join('\n')+'\n';
const projectRoot=path.resolve(__dirname,'..');
const out=path.join(projectRoot,'data','sample','events.csv');fs.writeFileSync(out,csv,'utf8');
fs.writeFileSync(path.join(projectRoot,'data','sample','README.md'),`# Bundled demo data\n\nThis deterministic simulated dataset was generated with seed 20261115 for CommerceLab. It is shaped to the documented normalized GA4 export schema but is not a copy or extract of Google's public GA4 sample. It contains ${events.length.toLocaleString()} events across ${firstVisitSeen.size} observed user IDs (sampled from a pool of ${users.length} possible user IDs) and 2020-11-01 through 2021-01-31. Run the generator script to reproduce it.\n`,'utf8');
console.log(`Wrote ${events.length} generated event rows to ${out}`);
