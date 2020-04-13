import base64
import io
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import scale
import arviz
import re
import tqdm
import sys

# TODO: KMeans hot shown in function
from sklearn.linear_model import ARDRegression, BayesianRidge
import pymc3 as pm
import matplotlib.pyplot as plt
# from matplotlib.figure import Figure
from sklearn.preprocessing import MinMaxScaler, StandardScaler, Normalizer
import logging
# StandardScaler for columns and Normalizer for rows

import time


color_scale = 'YlOrRd'


def process_data_for_modeling(df,
                              target_col,
                              numeric_feature_df,  # modify the function to deal with []!!!!!
                              cat_feature_df,  # modify the function to deal with []!!!!!
                              ):
    numeric_feature_list = numeric_feature_df['Feature'].tolist()
    cat_feature_list = cat_feature_df['Feature'].tolist()
    df = df[list(set(numeric_feature_list + cat_feature_list + [target_col]))]
    
    if cat_feature_list:

        # df_tranformed_dummy = pd.get_dummies(df[cat_feature_list])
        # #
        # dummy_tranformed_names = ["{}".format(i) for i in df_tranformed_dummy.columns]
        # df_tranformed_dummy.columns = dummy_tranformed_names
        # df = pd.concat([df, df_tranformed_dummy], axis=1)

        cols_modeling_list = numeric_feature_list + cat_feature_list + [target_col]

        dependent_variable_list = numeric_feature_list + cat_feature_list
    else:
        cols_modeling_list = numeric_feature_list + [target_col]

        dependent_variable_list = numeric_feature_list

    # TODO validate df_temp
    # numeric features
    df_temp = df[cols_modeling_list].values
    df[cols_modeling_list] = pd.DataFrame(df_temp)

    final_feature_list = cols_modeling_list
    print("Final_Feature_List")
    print(final_feature_list)

    df = df[final_feature_list]

    # special characters check

    df = df.rename(columns=lambda x: re.sub(r'\W+', '', x))

    # final_feature_list = [label_col] + final_feature_list
    # print('final_feature_list')
    # print(final_feature_list)
    print("process%%%",df)
    return df, dependent_variable_list


def parse_contents(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)

    try:

        if "csv" in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        elif "xls" in filename:
            df = pd.read_excel(io.BytesIO(decoded))

        elif "json" in filename:
            df = pd.read_json(contents)

        elif "txt" or "tsv" in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter=r"\s+")

        else:
            return []

        # df = df.rename(columns=lambda x: re.sub(r'^[a-z0-9A-Z_]', '', x))
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.replace(r"[^a-zA-Z\d\_]+", "")
        # df.columns = df.columns.str.replace(r"[^a-zA-Z\d]+", "")
        
    except Exception as e:
        print(e)

    return df.to_json()


def bayesian_regression_modeling(df,
                                 label_col,
                                 target_col,
                                 prior_distribution_list,
                                 draw_sample=1000,
                                 chains=2,
                                 scaling_opt=3):
    """

    :param df:
    :param label_col:
    :param target_col:
    :param model_option:
    :param draw_sample:
    :param chains:
    :param alpha_1:
    :param alpha_2:
    :param lambda_1:
    :param lambda_2:
    :return: MCMC mean trace array, MCMC visualization img source
    """
    # test: using scaling
    n_individuals = len(df)
    print("scale@@@@@",df)
    if scaling_opt == 1:
        df[df.columns] = StandardScaler().fit_transform(df[df.columns])
    elif scaling_opt == 2:
        df[df.columns] = MinMaxScaler().fit_transform(df[df.columns])
    elif scaling_opt == 3:
        df[df.columns] = df[df.columns]
    feature_list = df.columns
    feature_list = [i for i in feature_list if i != label_col]
    print(feature_list)
    print("Model datasett:BHJLK")
    print(df)

    # Using PyMC3
    # formula = str(target_col)+' ~ '+' + '.join(['%s' % variable for variable in label_col])

    # degree of freedom
    # nu = len(df[label_col].count(axis=1)) - len(df[label_col].count(axis=0))

    # TODO: add student-T distribution as priors for each feature
    # get degree of freedom
    if len(df[label_col].count(axis=1)) >= len(df[label_col].count(axis=0)):
        nu = len(df[label_col].count(axis=1)) - len(df[label_col].count(axis=0))
    else:
        nu = 0

    print("Degree of Freedom:")
    print(nu)

    # with pm.Model() as normal_model:
    #     start = time.time()
    #
    #     # intercept = pm.StudentT('Intercept', nu=nu, mu=0, sigma=1)
    #     # sigma = pm.HalfCauchy("sigma", beta=10, testval=1.)
    #     # pass in a prior mean & coefficient list
    #
    #
    #     family = pm.glm.families.Normal()
    #     pm.GLM.from_formula(formula, data=df, family=family)
    #     trace = pm.sample(draws=draw_sample, chains=chains, tune=500, random_seed=23)
    #     end = time.time()
    #     print("Time elasped: {} seconds.".format(end-start))
    #     print("DONE normal_trace")
    with pm.Model() as model:
        fea_list = [variable for variable in label_col]
        print(fea_list)
        pm_list = []
        i = 0
        for prior_dist in prior_distribution_list:
            #         for j in range(len(fea_list)):
            
            for type,prior in prior_dist.items():
                if type != "Target" and prior == "Normal":

                    #             print(fea_list[j])
                    pm_list.append(pm.Normal(str(fea_list[i])))
                    i += 1
                elif type != "Target" and prior == "Student T":   
                
                    pm_list.append(pm.StudentT(str(fea_list[i]), nu=nu))
                    i += 1
                elif type != "Target" and prior == "Skew Normal": 
                    pm_list.append(pm.SkewNormal(str(fea_list[i])))
                    i += 1
            # for i, item in enumerate(prior_distribution_list):Skew Normal
            #     setattr(sys.modules[__name__], 'beta{0}'.format(i), item)
            # hyper_sigma = pm.HalfNormal('hyper_sigma', sd=3)
        sigma = pm.HalfCauchy('sigma', beta=10, testval=1.)
        intercept = pm.Normal('Intercept', 0, sigma=20)

        # setting the distribution mean for the predictor
        mu = intercept
        print("MUUU")
        print(mu)
        for i in range(len(pm_list)):
            print("PM LIST i")
            print(pm_list[i])
            print("DF[FEA_LIST]")
            print(df[fea_list[i]])
            mu += pm_list[i] * df[fea_list[i]].to_numpy()
            #mu += pm_list[i] * np.ones(df[fea_list[i]].to_list())
            print(df[fea_list[i]].to_numpy())
        for prior_dist in prior_distribution_list:
            for type,prior in prior_dist.items():
                 if type == "Target" and prior == "Normal":
                    print("Target Normal")
                    likelihood = pm.Normal(str(target_col), mu=mu, sigma=sigma, observed=df[target_col])
                 elif type == "Target" and prior == "Student T":
                    print("Target Student")
                    likelihood = pm.StudentT(str(target_col), nu = nu , mu=mu, sd=sigma, shape = n_individuals)
                 elif type == "Target" and prior == "Skew Normal":
                    print("Target Skew")
                    mu = pm.Uniform('lambda_bl', 0., draw_sample)
                    likelihood = pm.SkewNormal(str(target_col),mu=mu, sigma=sigma,tau=None, alpha=1, sd=3)
                 elif type == "Target" and prior == nan:
                    print("Target Nan")
                    likelihood = pm.Normal(str(target_col), mu=mu, sigma=sigma, observed=df[target_col])
        #means = pm.StudentT('means', nu = nu, mu = hyper_mean, sd = hyper_sigma, shape = n_individuals)
        #SkewNormal(mu=0.0, sigma=None, tau=None, alpha=1, sd=None, *args, **kwargs)
        trace = pm.sample(draws=draw_sample, chains=chains, random_seed=23,progressbar=True)
        img_source = save_mat_fig(trace, gtype='traceplot')
        posterior_dist = save_mat_fig(trace, gtype='posterior')

        # return np.array([np.mean(trace[variable]) for variable in trace.varnames]), img_source, posterior_dist
        return trace, img_source, posterior_dist
        # return np.array([normal_trace[variable] for variable in normal_trace.varnames]), "data:image/png;base64,{}".format(data)

    # elif model_option == 2:
    #     clf = BayesianRidge(alpha_1=alpha_1,
    #                         lambda_1=lambda_1,
    #                         alpha_2=alpha_2,
    #                         lambda_2=lambda_2,
    #                         normalize=True).fit(df[label_col], df[target_col])
    #     return clf.coef_, [], []


def save_mat_fig(trace_array, gtype="traceplot"):
    """
    save the traceplot array to an image source
    :param trace_array:
    :return:
    """
    # fig = Figure()
    if gtype == "traceplot":
        print("ENTER save_traceplot")
        pm.traceplot(trace_array, figsize=(12,12))
        print("PLT.GCF()")
        fig = plt.gcf()
        print("FIGURE")
        buf = io.BytesIO()
        print("BUFF")
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("utf8")
    elif gtype == "posterior":
        print("ENTER plot_posterior")
        pm.plot_posterior(trace_array, figsize=(12,12))
        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        data = base64.b64encode(buf.getbuffer()).decode("utf8")
    else:
        data = []
    return "data:image/png;base64,{}".format(data)


def create_modeling_feature_tbl_from_uploaded_file(df):
    df_type = pd.DataFrame(df.dtypes).reset_index(drop=False)
    df_type.columns = ['Feature', 'type']
    df_type['Type'] = 'Numeric'
    df_type.loc[df_type.type == 'object', 'Type'] = 'Categorical'
    df_type['Weight'] = 1
    print(df_type)
    return df_type[['Feature', 'Type', 'Weight']]

