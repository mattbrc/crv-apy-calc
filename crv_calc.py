
from requests import Request, Session
import json
import pandas as pd
import datetime as dt


class GetAPIData:

    def get_crv_price(self, api, params, headers, session):
        response = session.get(f"{api}", params=params)
        data = json.loads(response.text)
        global crv_price
        if response.status_code == 200:
            crv_price = float(json.dumps(data['data']['CRV'][0]['quote']
                                         ['USD']['price'], indent=4))
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

    def get_cvx_price(self, api, params, headers, session):
        response = session.get(f"{api}", params=params)
        data = json.loads(response.text)
        global cvx_price
        if response.status_code == 200:
            cvx_price = float(json.dumps(data['data']['CVX'][0]['quote']
                                         ['USD']['price'], indent=4))
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

    def get_vecrv_supply(self, api, session):
        response = session.get(f"{api}")
        data = json.loads(response.text)
        global vecrv_supply
        if response.status_code == 200:
            vecrv_supply = int(data['result']) / 1000000000000000000
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

    def crv_calc(self, crv_pd, tot_vecrv, crv_p, pool, no):
        daily_minted_crv_per_vecrv = crv_pd/tot_vecrv
        yearly_minted_crv_per_vecrv = daily_minted_crv_per_vecrv*365
        yearly_minted_crv_per_vecrv_USD = round(
            yearly_minted_crv_per_vecrv*crv_p, 2)
        yearly_minted_cvx_per_crv_USD = round(
            yearly_minted_crv_per_vecrv_USD * (1 + 0.2702), 2)

        pool_size = pool
        no_crv = no

        apy = ((pool_size + (no_crv * yearly_minted_crv_per_vecrv_USD) +
                (no_crv * yearly_minted_cvx_per_crv_USD))/pool_size) - 1
        apy_no_cvx_rewards = (
            (pool_size+(no_crv*yearly_minted_crv_per_vecrv_USD))/pool_size)-1

        print('CRV per Day: ' + str(crv_pd) + '\n' + 'CRV minted per veCRV per Day: ' + str(daily_minted_crv_per_vecrv) + '\n' + 'CRV minted per veCRV per Year: ' + str(yearly_minted_crv_per_vecrv) + '\n' + '($) CRV minted per veCRV per Day: ' +
              str(yearly_minted_crv_per_vecrv_USD) + '\n' + '($) CRV minted per veCRV per Year: ' + str(yearly_minted_cvx_per_crv_USD) + '\n' + 'APY: ' + str(apy) + '\n' + 'APY without CSV Rewards: ' + str(apy_no_cvx_rewards))
        return apy, apy_no_cvx_rewards

    def cvx_calc(self, n_cvx_in_convexfi, tl_cvx, crv_pd, crv_p, pool, no):
        vecrv_per_cvx = n_cvx_in_convexfi/tl_cvx

        daily_minted_crv_per_cvx = crv_pd/92770369

        yearly_minted_crv_per_cvx = daily_minted_crv_per_cvx*365

        yearly_minted_crv_per_cvx_USD = round(
            yearly_minted_crv_per_cvx*crv_p, 2)
        yearly_minted_cvx_per_crv_USD = round(0, 2)

        pool_size = pool
        no_crv = no

        apy = ((pool_size + (no_crv*yearly_minted_crv_per_cvx_USD) +
                (no_crv*yearly_minted_cvx_per_crv_USD))/pool_size)-1

        print('veCRV per CVX: ' + str(vecrv_per_cvx) + '\n' + 'CRV minted per CVX per Day: ' + str(daily_minted_crv_per_cvx) + '\n' + 'CRV minted per CVX per Year: ' +
              str(yearly_minted_crv_per_cvx) + '\n' + '($) CRV minted per CVX per Year: ' + str(yearly_minted_crv_per_cvx_USD) + '\n' + 'APY: ' + str(apy))

        return apy

    def __init__(self, cmc_api, etherscan_api):
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': '49d66445-61cf-4559-833e-2a90857e88fe',
        }
        crv_parameters = {
            'symbol': 'CRV',
            'convert': 'USD'
        }
        cvx_parameters = {
            'symbol': 'CVX',
            'convert': 'USD'
        }
        session = Session()
        session.headers.update(headers)
        self.get_crv_price(cmc_api, crv_parameters, headers, session)
        self.get_cvx_price(cmc_api, cvx_parameters, headers, session)
        self.get_vecrv_supply(etherscan_api, session)

        crv_emissions = {'date': [dt.datetime(2022, 9, 11), dt.datetime(2023, 9, 10)],
                         'state': [521530493, 874809759]}

        crv_em = pd.DataFrame(crv_emissions)

        crv_em_date_diff = crv_em['date'][1] - crv_em['date'][0]
        crv_em_state_diff = crv_em['state'][1] - crv_em['state'][0]
        crv_per_day = crv_em_state_diff/crv_em_date_diff.days
        no_crv_lock_in_convexfi = 275782038.667
        total_locked_cvx = 47154292
        print('\n')
        print('First function output:')
        a, b = self.crv_calc(crv_per_day, vecrv_supply,
                             crv_price, 10000000, 500000)
        print('This function returns CRV APY: ' + str(a) +
              ' and CRV APY without CVX Rewards: ' + str(b))

        print('\n')
        print('Second function output:')
        cxv_apy = self.cvx_calc(no_crv_lock_in_convexfi, total_locked_cvx,
                                crv_per_day, crv_price, 10000000, 100000)
        print('This function returns the CXV APY from the "Base" tab in the "CVX Heatmap" GSheet: ' + str(cxv_apy))


if __name__ == "__main__":
    get_data = GetAPIData(
        "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest",
        "https://api.etherscan.io/api?module=stats&action=tokensupply&contractaddress=0x5f3b5DfEb7B28CDbD7FAba78963EE202a494e2A2&apikey=UKFQBJ9MX5SJ4U8ZYPD879QTK48VHURZRQ"
    )
