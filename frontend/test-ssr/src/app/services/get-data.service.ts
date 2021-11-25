import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AppDataService } from './app-data.service';
import { Person } from '../entities/person';

@Injectable({
  providedIn: 'root'
})
export class GetDataService {

  public apiUrl: string = 'https://dari-cosmetics.ru/api/';

  constructor(
    private http: HttpClient
  ) { }

  getCatalog() {
    return this.http.get<any>(this.apiUrl + 'shop/catalog');
  }

  getCatalogCategory(slug) {
    return this.http.get<any>(this.apiUrl + 'shop/categories/' + slug);
  }

  getCatalogSubcategory(slug) {
    return this.http.get<any>(this.apiUrl + 'shop/subcategories/' + slug);
  }

  getProductInfo(id_product) {
    return this.http.get<any>(this.apiUrl + 'shop/products/' + id_product);
  }

  getProductComments(id_product) {
    return this.http.get<any>(this.apiUrl + 'shop/prod_feedback/' + id_product);
  }

  getComments(){
    return this.http.get<any>(this.apiUrl + 'shop/prod_feedback');
  }

  getProductsList(product_list: string) {
    return this.http.get<any>(this.apiUrl + 'shop/products?' + product_list);
  }

  getComponentInfo(id: string) {
    return this.http.get<any>(this.apiUrl + 'shop/components/' + id);
  }

  facebookAuth(token: any, backend: string) {
    return this.http.post<any>(this.apiUrl + 'appuser/auth/social', {access_token: token, backend: backend});
  }

  vkAuth(code: string) {
    return this.http.post<any>(this.apiUrl + 'appuser/auth/social', {code: code, backend: 'vk-oauth2'});
  }

  signUpUser(
    username: string, 
    email: string, 
    password: string, 
    password2: string, 
    lastName: string = '', 
    firstName: string = '', 
    secondName: string = '', 
    phone: string) {
    return this.http.post<any>(this.apiUrl + 'appuser/users',{
      username: username,
      password1: password,
      password2: password2,
      last_name: lastName,
      first_name: firstName,
      patronymic: secondName,
      email: email,
      phone: phone  
    })
  }

  loginUser(username: string, pass: string) {
    return this.http.post<any>(this.apiUrl + 'appuser/login', {
      username: username,
      password: pass
    })
  }

  /** Programs */
  getAllPrograms(limit: number = 100) {
    return this.http.get<any>(this.apiUrl + 'shop/kits?limit=' + limit);
  }

  getProgramData(id: string) {
    return this.http.get<any>(this.apiUrl + 'shop/kits/' + id);
  }

  getProgramFeedback(id: string) {
    return this.http.get<any>(this.apiUrl + 'shop/kit_feedback/' + id);
  }

  getProdFeedback() {
    return this.http.get<any>(this.apiUrl + 'shop/prod_feedback');
  }

  /** User info*/
  getUserOrders(token: string, limit: number = 100, offset: number = 0) {
    return this.http.get<any>(this.apiUrl + 'shop/orders?limit=' + limit + '&offset=' + offset,{ headers: {'Authorization': token}});
  }

  getRefOrders(limit: number = 100, offset: number = 0) {
    if (AppDataService.user && AppDataService.userLoggedIn) {
      return this.http.get<any>(this.apiUrl + 'appuser/ref_orders?limit=' + limit + '&offset=' + offset, {headers: {'Authorization': AppDataService.userToken}});
    } else {
      return this.http.get<any>(this.apiUrl + 'appuser/ref_orders?limit=' + limit + '&offset=' + offset);
    }
  }

  getReferals(limit: number = 100, offset: number = 0) {
    return this.http.get<any>(this.apiUrl + 'appuser/referrals?limit=' + limit + '&offset=' + offset, { headers: {'Authorization': AppDataService.userToken}})
  }

  getUserInfo(token: string, user_id: any) {
    return this.http.get<any>(this.apiUrl + 'appuser/users/' + user_id, {headers: {'Authorization': token}});
  }

  changeProfile(user: any) {
    return this.http.put<Person>(this.apiUrl + 'appuser/users/' + user.id, {
      username: user.username,
      email: user.email,
      phone: user.phone,
      last_name: user.last_name,
      first_name: user.first_name,
      patronymic: user.patronymic,
      is_partner: user.is_partner,
      is_jur: user.is_jur,
      sms_notice: user.sms_notice,
      email_notice: user.email_notice,
      addresses: user.addresses,
      phys_profile: user.phys_profile,
      jur_profile: user.jur_profile  
    }, { headers: {'Authorization': AppDataService.userToken} })
  }

  changePassword(newpas: string) {
    return this.http.post<any>(this.apiUrl + 'appuser/change_password', {
      new_password1: newpas,
      new_password2: newpas
    }, { headers: {'Authorization': AppDataService.userToken} })
  }

  resetPassword(email: string) {
    return this.http.post<any>(this.apiUrl + 'appuser/password/reset', { email: email });
  }

  setNewPassword(id: string, newpas: string) {
    return this.http.post<any>(this.apiUrl + 'appuser/password/confirm/' + id, { new_password1: newpas, new_password2: newpas });
  }

  bonusToBalance(sum: number) {
    return this.http.post<any>(this.apiUrl + 'appuser/bonus_to_balance/', { amount: sum }, {headers: {'Authorization': AppDataService.userToken}})
  }

  changeAvatar(filename: string, img: any) {
    return this.http.put<any>(this.apiUrl + 'appuser/avatar_upload/' + filename, img, {headers: {'Authorization': AppDataService.userToken}})
  }

  /** delivery*/
  dadataQuery(token: string, query: any) {
    return this.http.post<any>('https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address', query , {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Token ' + token
      }
    })
  }

  calcShipping(orderInfo) {
    return this.http.post<any>(this.apiUrl + 'shop/calc_shipping', orderInfo)
  }

  getDeliveryPoints(post_code: string, type: string = 'PVZ') {
    return this.http.get<any>(this.apiUrl + 'shop/delivery_points?postcode=' + post_code + '&point_type=' + type);
  }

  getCountriesList() {
    return this.http.get<any>(this.apiUrl + 'shop/countries');
  }

  saveOrder( edit: any = false, order_info: any) {
    if (AppDataService.user && AppDataService.userLoggedIn) {
      if (edit) {
        return this.http.put<any>(this.apiUrl + 'shop/orders/' + edit, order_info, {headers: {'Authorization': AppDataService.userToken}});
      } else {
        return this.http.post<any>(this.apiUrl + 'shop/orders', order_info, {headers: {'Authorization': AppDataService.userToken}});
      }
    } else {
      return this.http.post<any>(this.apiUrl + 'shop/orders', order_info );
    }
  }

  getOrderData(id: string) {
    return this.http.get<any>(this.apiUrl + 'shop/orders/' + id);
  }

  setReferal(id: string) {
    return this.http.get<any>(this.apiUrl + 'ref/' + id);
  }

  getPromocodeInfo(code: string) {
    return this.http.get(this.apiUrl + 'shop/promo', { params: { code: code }});
  }

  getBonusHistory() {
    return this.http.get(this.apiUrl + 'appuser/bonus-history?limit=20', { headers: {'Authorization': AppDataService.userToken} });
  }

  /** blog */
  getBlog() {
    return this.http.get<any>(this.apiUrl + 'blog/articles?limit=100');
  }

  getArticleData(article_id: string) {
    return this.http.get<any>(this.apiUrl + 'blog/articles/' + article_id);
  }

  getMainSlides() {
    return this.http.get<any>(this.apiUrl + 'shop/slides');
  }

  getPaymentLink(order_id: string, shipping: number = 0) {
    return this.http.get<any>(this.apiUrl + 'shop/order_payment/' + order_id + '?bonus_amount=0&deposit_amount=0&shipping_amount=' + shipping);
  }

  getPaymentLinkUser(order_id: string, shipping: number = 0, bonus: number = 0, deposit: number = 0) {
    return this.http.get<any>(this.apiUrl + 'shop/order_payment/' + order_id + '?bonus_amount=' + bonus + '&deposit_amount=' + deposit + '&shipping_amount=' + shipping, {headers: {'Authorization': AppDataService.userToken}})
  }

  /** User advices*/
  sendProductAdvice(id: string, text: string, url: string, rating: number) {
    return this.http.post<any>(this.apiUrl + 'shop/prod_feedback', {text: text, product: id, video_link: url, rating: rating}, {headers: {'Authorization': AppDataService.userToken}});
  }

  sendKitAdvice(id: string, text: string, url: string) {
    return this.http.post<any>(this.apiUrl + 'shop/kit_feedback', {text: text, kit: id, video_link: url}, {headers: {'Authorization': AppDataService.userToken}});
  }

  /**User feedback */
  sendFeedback(name: string, phone: string, age: number, text: string, email: string, type: string) {
    return this.http.post<any>(this.apiUrl + 'shop/advice', {
      name: name,
      phone: phone,
      age: (age)? age : undefined,
      text: text,
      email: email,
      advice_type: type
    })
  }

  getAdviceTypes() {
    return this.http.get<any>(this.apiUrl + 'shop/advice_types');
  }

  /**Events */
  getEventsList() {
    return this.http.get<any>(this.apiUrl + 'shop/events');
  }

  getEventData(id: string) {
    return this.http.get<any>(this.apiUrl + 'shop/events/' + id);
  }

  /*Insta*/
  getInstaFeed(){
    return this.http.get<any>('https://www.instagram.com/daricosmetics/?__a=1');
  }

}
